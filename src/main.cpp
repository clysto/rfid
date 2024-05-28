#include <fmt/core.h>
#include <gnuradio/block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/top_block.h>
#include <omp.h>

#include <algorithm>
#include <cmath>
#include <deque>
#include <eigen3/Eigen/Dense>
#include <iostream>
#include <numeric>
#include <vector>

namespace config {
const float SAMP_RATE = 2e6;
const float PULSE_THRESHOLD = 0.02;  // The threshold value for detecting pulses.
const int READER_MIN_PULSES = 5;     // The minimum number of pulses required for a valid reader signal.
const int N_PULSE_WIDTH = 24;        // pw = 12us = 24 samples @ 2e6 samp/s
const int N_T1 = 460;
const int N_RN16_FRAME = 1250;
const double CENTER_MIN_RHO = 10;   // The minimum rho value for a center to be considered valid.
const double CLUSTER_MIN_PROB = 1;  // The minimum probability for a sample to be considered as a valid.
}  // namespace config

enum level_t {
  LOW,
  HIGH,
};

enum status_t {
  SEEK_READER_COMMAND,
  PROCESSING_RN16,
};

class BivariateNormal {
 public:
  BivariateNormal(double variance1, double variance2) : variances(variance1, variance2) {
    // 确保方差为正
    if (variance1 <= 0 || variance2 <= 0) {
      throw std::invalid_argument("Variances must be positive");
    }
    // 计算归一化常数
    norm_const = 1.0 / (2.0 * M_PI * std::sqrt(variance1 * variance2));
  }

  double pdf(const Eigen::Vector2d &x, const Eigen::Vector2d &mean) const {
    Eigen::Vector2d diff = x - mean;
    double exponent = -0.5 * (diff.array() * diff.array() / variances.array()).sum();
    double pdf_value = norm_const * std::exp(exponent);
    return pdf_value;
  }

 private:
  Eigen::Vector2d variances;
  double norm_const;
};

void processing_rn16(const std::vector<gr_complex> &frame, const std::deque<gr_complex> &dc_samples) {
  int N = frame.size();
  auto logger = std::make_shared<gr::logger>("processing_rn16");
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

  std::cout << mag_var << ", " << phase_var << std::endl;

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
  while (j <= 4) {
    if (rhos[ordlambdas[i]] > config::CENTER_MIN_RHO) {
      centers_index[j++] = ordlambdas[i];
    }
    i++;
  }

  // 使用高斯分布进行聚类
  std::vector<int> labels(N);
  auto norm = BivariateNormal(mag_var, phase_var);
#pragma omp parallel for
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
    labels[i] = max_pdf > config::CLUSTER_MIN_PROB ? label : -1;
  }
  for (int i = 0; i < N; i++) {
    std::cout << labels[i] << ",";
  }
  exit(0);
}

class my_block : public gr::block {
 private:
  status_t d_status = SEEK_READER_COMMAND;
  int d_pulse_count = 0;
  level_t d_signal_level = HIGH;
  int d_pulse_nsamples = 0;
  std::vector<gr_complex> d_rn16_frame = std::vector<gr_complex>(config::N_RN16_FRAME);
  std::deque<gr_complex> d_dc_samples = std::deque<gr_complex>();

 public:
  typedef std::shared_ptr<my_block> sptr;

  static sptr make() { return gnuradio::make_block_sptr<my_block>(); }

  my_block() : gr::block("my_block", gr::io_signature::make(0, -1, 8), gr::io_signature::make(0, 0, 0)) {}

  int general_work(int noutput_items, gr_vector_int &ninput_items, gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items) {
    gr_complex *in = (gr_complex *)input_items[0];
    float sample_ampl;
    for (int i = 0; i < ninput_items[0]; i++) {
      switch (d_status) {
        case SEEK_READER_COMMAND:
          if (d_dc_samples.size() >= config::N_T1 / 2) {
            d_dc_samples.pop_front();
          }
          d_dc_samples.push_back(in[i]);
          sample_ampl = std::abs(in[i]);
          d_pulse_nsamples++;
          // negative edge
          if (sample_ampl <= config::PULSE_THRESHOLD && d_signal_level == HIGH) {
            d_signal_level = LOW;
            d_pulse_nsamples = 0;
          }
          // positive edge
          if (sample_ampl > config::PULSE_THRESHOLD && d_signal_level == LOW) {
            d_signal_level = HIGH;
            if (d_pulse_nsamples > config::N_PULSE_WIDTH / 2) {
              d_pulse_count++;
            } else {
              d_pulse_count = 0;
            }
            d_pulse_nsamples = 0;
          }
          if (d_pulse_nsamples > config::N_T1 && d_signal_level == HIGH && d_pulse_count > config::READER_MIN_PULSES) {
            d_rn16_frame.clear();
            d_status = PROCESSING_RN16;
            d_logger->info("================ RN16 Frame ================");
            d_logger->info("start_index: {}", i + nitems_read(0) + 1);
          }
          break;

        case PROCESSING_RN16:
          if (d_rn16_frame.size() < config::N_RN16_FRAME) {
            d_rn16_frame.push_back(in[i]);
          } else {
            d_logger->info("end_index: {}", i + nitems_read(0));

            processing_rn16(d_rn16_frame, d_dc_samples);

            d_signal_level = HIGH;
            d_pulse_count = 0;
            d_pulse_nsamples = 0;
            d_status = SEEK_READER_COMMAND;
          }
          break;

        default:
          break;
      }
    }

    consume(0, ninput_items[0]);
    return 0;
  }
};

int main(int argc, char *argv[]) {
  gr::top_block_sptr tb = gr::make_top_block("main");
  auto source = gr::blocks::file_source::make(8, argv[1], false);
  auto my = my_block::make();
  tb->connect(source, 0, my, 0);
  tb->start();
  tb->wait();
  return 0;
}
