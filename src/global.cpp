#include "global.hpp"

namespace config {
const float SAMP_RATE = 2e6;
const float PULSE_THRESHOLD = 0.02;
const int READER_MIN_PULSES = 5;
const int N_PULSE_WIDTH = 24;
const int N_T1 = 460;
const int N_RN16_FRAME = 1150;
const double CENTER_MIN_RHO = 10;
const double CLUSTER_MIN_PROB = 1;
const int SPS = 25;
const int FM0_PREAMBLE[] = {1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1};
const int FM0_PREAMBLE_LEN = 12;
const int CORRELATION_LEN = 100;
}  // namespace config