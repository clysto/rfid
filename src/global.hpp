#pragma once

namespace config {
extern const float SAMP_RATE;
extern const float PULSE_THRESHOLD;  // The threshold value for detecting pulses.
extern const int READER_MIN_PULSES;  // The minimum number of pulses required for a valid reader signal.
extern const int N_PULSE_WIDTH;      // pw = 12us = 24 samples @ 2e6 samp/s
extern const int N_T1;
extern const int N_RN16_FRAME;         // (12 + 32) * 25 = 1100 samples
extern const double CENTER_MIN_RHO;    // The minimum rho value for a center to be considered valid.
extern const double CLUSTER_MIN_PROB;  // The minimum probability for a sample to be considered as a valid.
extern const int SPS;
extern const int FM0_PREAMBLE[];
extern const int FM0_PREAMBLE_LEN;
extern const int CORRELATION_LEN;
}  // namespace config
