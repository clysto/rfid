#include <gnuradio/block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/top_block.h>

#include <iostream>
#include <vector>

#include "extract_inter_channel.hpp"
#include "rfid_block.hpp"

void p(const std::deque<gr_complex> &frame, const std::deque<gr_complex> &dc_samples, gr_complex dc_est,
       gr_complex h_est) {
  std::vector<int> labels;
  auto s_int = extract_inter_channel(frame, dc_samples, dc_est, h_est, labels);
  std::cout << "s_int: mag=" << std::abs(s_int) << " phase=" << std::arg(s_int) << std::endl;
}

int main(int argc, char *argv[]) {
  gr::top_block_sptr tb = gr::make_top_block("main");
  auto source = gr::blocks::file_source::make(8, argv[1], false);
  auto b = rfid_block::make(p);
  tb->connect(source, 0, b, 0);
  tb->start();
  tb->wait();
  return 0;
}
