#include <gnuradio/block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/top_block.h>

#include <iostream>

#include "cnpy.hpp"
#include "rfid_block.hpp"

std::vector<gr_complex> frames;

void p(const std::deque<gr_complex> &frame, const std::deque<gr_complex> &dc_samples, gr_complex dc_est,
       gr_complex h_est) {
  if (frame.size() != config::N_RN16_FRAME) {
    return;
  }
  frames.insert(frames.end(), frame.begin(), frame.end());
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    std::cerr << "Usage: " << argv[0] << " <input_file> <output_file>" << std::endl;
    return 1;
  }

  gr::top_block_sptr tb = gr::make_top_block("main");
  auto source = gr::blocks::file_source::make(8, argv[1], false);
  auto b = rfid_block::make(p);
  tb->connect(source, 0, b, 0);
  tb->start();
  tb->wait();

  cnpy::npy_save(argv[2], frames.data(),
                 {frames.size() / config::N_RN16_FRAME, static_cast<size_t>(config::N_RN16_FRAME)}, "w");

  return 0;
}
