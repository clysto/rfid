#pragma once

#include <gnuradio/gr_complex.h>

#include <deque>
#include <eigen3/Eigen/Dense>

class BivariateNormal {
 public:
  BivariateNormal(double variance1, double variance2);

  double pdf(const Eigen::Vector2d &x) const;

 private:
  Eigen::Vector2d variances;
  double norm_const;
};

gr_complex extract_inter_channel(const std::deque<gr_complex> &frame, const std::deque<gr_complex> &dc_samples,
                                 gr_complex dc_est, gr_complex h_est, std::vector<int> &labels);
