#include "rfid_block.hpp"

#include <algorithm>
#include <numeric>

#include "extract_inter_channel.hpp"

rfid_block::rfid_block() : gr::block("rfid_block", gr::io_signature::make(0, -1, 8), gr::io_signature::make(0, 0, 0)) {
  for (int i = 0; i < config::FM0_PREAMBLE_LEN; i++) {
    for (int j = 0; j < config::SPS; j++) {
      d_preamble_samples.push_back(gr_complex(config::FM0_PREAMBLE[i], 0));
    }
  }
}

int rfid_block::general_work(int noutput_items, gr_vector_int &ninput_items, gr_vector_const_void_star &input_items,
                             gr_vector_void_star &output_items) {
  gr_complex *in = (gr_complex *)input_items[0];
  float sample_ampl;
  int consumed = 0;
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
          d_corr = 0;
          d_corr_index = 0;
          d_rn16_start_index = 0;
          d_dc_est = std::accumulate(d_dc_samples.begin(), d_dc_samples.end(), gr_complex(0, 0)) /
                     gr_complex(d_dc_samples.size(), 0);
          d_status = SYNC_RN16;
        }
        break;

      case SYNC_RN16:
        d_rn16_frame.push_back(in[i]);

        if (d_rn16_frame.size() >= d_corr_index + d_preamble_samples.size()) {
          gr_complex corr = 0;
#pragma omp parallel for reduction(+ : corr)
          for (int j = 0; j < d_preamble_samples.size(); j++) {
            corr += (d_rn16_frame[d_corr_index + j] - d_dc_est) * d_preamble_samples[j];
          }
          d_corr_index++;
          if (std::abs(corr) > d_corr) {
            d_corr = std::abs(corr);
            d_rn16_start_index = d_corr_index;
          }
        }

        // 同步到 RN16 帧的前导码
        if (d_corr_index >= config::CORRELATION_LEN) {
          // 计算信道估计 h_est
          d_h_est = 0;
          int ones_in_preamble = 0;
#pragma omp parallel for reduction(+ : d_h_est, ones_in_preamble)
          for (int j = 0; j < config::FM0_PREAMBLE_LEN; j++) {
            if (config::FM0_PREAMBLE[j] == 1) {
              d_h_est += d_rn16_frame[d_rn16_start_index + j * config::SPS + config::SPS / 2];
              ones_in_preamble++;
            }
          }
          d_h_est /= gr_complex(ones_in_preamble, 0);

          d_rn16_frame.erase(d_rn16_frame.begin(), d_rn16_frame.begin() + d_rn16_start_index);
          d_status = PROCESSING_RN16;
          d_logger->info("================ RN16 Frame ================");
          d_logger->info("start_index: {}", i + nitems_read(0) - d_rn16_frame.size() + 1);
        }

        break;

      case PROCESSING_RN16:
        if (d_rn16_frame.size() < config::N_RN16_FRAME) {
          d_rn16_frame.push_back(in[i]);
        } else {
          d_logger->info("end_index: {}", i + nitems_read(0));

          extract_inter_channel(d_rn16_frame, d_dc_samples, d_dc_est, d_h_est);

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
