#pragma once

#include <gnuradio/block.h>

#include "global.hpp"

enum level_t {
  LOW,
  HIGH,
};

enum status_t {
  SEEK_READER_COMMAND,
  SYNC_RN16,
  PROCESSING_RN16,
};

class rfid_block : public gr::block {
 private:
  status_t d_status = SEEK_READER_COMMAND;
  int d_pulse_count = 0;
  level_t d_signal_level = HIGH;
  int d_pulse_nsamples = 0;
  gr_complex d_dc_est = 0;
  gr_complex d_h_est = 0;
  float d_corr = 0;
  int d_corr_index = 0;
  int d_rn16_start_index = 0;
  std::deque<gr_complex> d_rn16_frame = std::deque<gr_complex>(config::N_RN16_FRAME);
  std::deque<gr_complex> d_dc_samples = std::deque<gr_complex>();
  std::vector<gr_complex> d_preamble_samples = std::vector<gr_complex>();

 public:
  typedef std::shared_ptr<rfid_block> sptr;

  static sptr make() { return gnuradio::make_block_sptr<rfid_block>(); }

  rfid_block();

  int general_work(int noutput_items, gr_vector_int &ninput_items, gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};
