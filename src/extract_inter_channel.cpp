#include "extract_inter_channel.hpp"

#include <omp.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>

#include "global.hpp"

BivariateNormal::BivariateNormal(double variance1, double variance2) : variances(variance1, variance2) {
  // 确保方差为正
  if (variance1 <= 0 || variance2 <= 0) {
    throw std::invalid_argument("Variances must be positive");
  }
  // 计算归一化常数
  norm_const = 1.0 / (2.0 * M_PI * std::sqrt(variance1 * variance2));
}

double BivariateNormal::pdf(const Eigen::Vector2d &x, const Eigen::Vector2d &mean) const {
  Eigen::Vector2d diff = x - mean;
  double exponent = -0.5 * (diff.array() * diff.array() / variances.array()).sum();
  double pdf_value = norm_const * std::exp(exponent);
  return pdf_value;
}

gr_complex extract_inter_channel(const std::deque<gr_complex> &frame, const std::deque<gr_complex> &dc_samples,
                                 gr_complex dc_est, gr_complex h_est) {
  int N = frame.size();
  Eigen::MatrixXd mag_phase(N, 2);
  Eigen::MatrixXd dc_mag_phase(dc_samples.size(), 2);
#pragma omp parallel for
  for (int i = 0; i < N; i++) {
    mag_phase(i, 0) = std::abs(frame[i]);
    mag_phase(i, 1) = std::arg(frame[i]);
  }
#pragma omp parallel for
  for (int i = 0; i < dc_samples.size(); i++) {
    dc_mag_phase(i, 0) = std::abs(dc_samples[i]);
    dc_mag_phase(i, 1) = std::arg(dc_samples[i]);
  }

  // 计算 DC 的相位方差和幅度方差
  double mag_mean = dc_mag_phase.col(0).mean();
  double mag_var = (dc_mag_phase.col(0).array() - mag_mean).square().sum() / (dc_mag_phase.rows() - 1);

  double phase_mean = dc_mag_phase.col(1).mean();
  double phase_var = (dc_mag_phase.col(1).array() - phase_mean).square().sum() / (dc_mag_phase.rows() - 1);

  double scale = mag_var / phase_var;

  // 计算距离矩阵
  auto mag_diff = mag_phase.col(0).replicate(1, N) - mag_phase.col(0).transpose().replicate(N, 1);
  auto phase_diff = mag_phase.col(1).replicate(1, N) - mag_phase.col(1).transpose().replicate(N, 1);
  auto dists = (mag_diff.array().square() + scale * phase_diff.array().square()).sqrt();

  // 自动计算截断距离 dc
  int position = static_cast<int>(N * (N - 1) * 0.02);
  Eigen::ArrayXd tt = Eigen::ArrayXd{dists.reshaped()};
  std::nth_element(tt.begin(), tt.begin() + position + N, tt.end());
  double dc = tt(position + N);

  Eigen::ArrayXd rhos(N);
  std::vector<int> ordrhos(N);
  Eigen::ArrayXd deltas(N);

  // 计算样本密度 rhos
#pragma omp parallel for
  for (int i = 0; i < N; i++) {
    rhos(i) = (-(dists.row(i).array() / dc).square()).exp().sum() - 1;
  }

  std::iota(ordrhos.begin(), ordrhos.end(), 0);
  std::sort(ordrhos.begin(), ordrhos.end(), [&rhos](int i1, int i2) { return rhos(i1) > rhos(i2); });

  // 计算相对距离 deltas
#pragma omp parallel for
  for (int i = 1; i < N; i++) {
    int index = ordrhos[i];
    std::vector<int> index_higher_rho(ordrhos.begin(), ordrhos.begin() + i);
    double min_dist = std::numeric_limits<double>::max();
    for (int j : index_higher_rho) {
      if (dists(index, j) < min_dist) {
        min_dist = dists(index, j);
      }
    }
    deltas(index) = min_dist;
  }
  deltas(ordrhos[0]) = deltas.maxCoeff();

  // 计算 lambdas
  auto lambdas = rhos * deltas;
  std::vector<int> ordlambdas(N);
  std::iota(ordlambdas.begin(), ordlambdas.end(), 0);
  std::sort(ordlambdas.begin(), ordlambdas.end(), [&lambdas](int i1, int i2) { return lambdas(i1) > lambdas(i2); });

  // 计算聚类中心
  std::vector<int> centers_index(4);
  int i = 0;
  int j = 0;
  while (j < 4) {
    if (rhos[ordlambdas[i]] > config::CENTER_MIN_RHO) {
      centers_index[j++] = ordlambdas[i];
    }
    i++;
  }

  gr_complex centers[4] = {0, 0, 0, 0};
  int nsamples[4] = {0, 0, 0, 0};

  // 使用高斯分布进行聚类
  std::vector<int> labels(N);
  auto norm = BivariateNormal(mag_var, phase_var);
#pragma omp parallel for reduction(+ : centers[ : 4], nsamples[ : 4])
  for (int i = 0; i < N; i++) {
    double max_pdf = -1;
    int label = -1;
    for (int j = 0; j < 4; j++) {
      auto p = norm.pdf(mag_phase.row(i), mag_phase.row(centers_index[j]));
      if (p > max_pdf) {
        max_pdf = p;
        label = j;
      }
    }
    // 计算聚类中心
    if (max_pdf > config::CLUSTER_MIN_PROB) {
      labels[i] = label;
      centers[label] += frame[i];
      nsamples[label]++;
    } else {
      labels[i] = -1;
    }
  }

  // 计算 LL, HH, LH, HL
  int ll_index = -1, hh_index = -1, lh_index = -1, hl_index = -1;
  float ll_dist = std::numeric_limits<float>::max();
  float hh_dist = std::numeric_limits<float>::max();

  for (int i = 0; i < 4; i++) {
    centers[i] /= nsamples[i];
    // 和 dc_est 最近的点为 LL
    if (std::abs(centers[i] - dc_est) < ll_dist) {
      ll_dist = std::abs(centers[i] - dc_est);
      ll_index = i;
    }
    // 和 h_est 最近的点为 HH
    if (std::abs(centers[i] - h_est) < hh_dist) {
      hh_dist = std::abs(centers[i] - h_est);
      hh_index = i;
    }
  }
  // 剩下的两个点分别为 LH 和 HL
  for (int i = 0; i < 4; i++) {
    if (i != ll_index && i != hh_index) {
      if (lh_index == -1) {
        lh_index = i;
      } else if (hl_index == -1) {
        hl_index = i;
      }
    }
  }

  // 计算互感向量
  gr_complex s_int = (centers[lh_index] - centers[ll_index]) + (centers[hl_index] - centers[ll_index]) -
                     (centers[hh_index] - centers[ll_index]);

  return s_int;
}
