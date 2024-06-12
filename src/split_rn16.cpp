#include <gnuradio/block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/top_block.h>

#include <iostream>

#include "cnpy.hpp"
#include "extract_inter_channel.hpp"
#include "rfid_block.hpp"

std::vector<gr_complex> frames;
std::vector<int> frames_labels;
std::vector<gr_complex> frames_dc;
std::vector<gr_complex> inter_est;

void p(const std::deque<gr_complex> &frame, const std::deque<gr_complex> &dc_samples, gr_complex dc_est,
       gr_complex h_est) {
  if (frame.size() != config::N_RN16_FRAME) {
    return;
  }
  frames_dc.insert(frames_dc.end(), dc_samples.begin(), dc_samples.end());
  frames.insert(frames.end(), frame.begin(), frame.end());
  std::vector<int> labels;
  auto s_int = extract_inter_channel(frame, dc_samples, dc_est, h_est, labels);
  frames_labels.insert(frames_labels.end(), labels.begin(), labels.end());
  inter_est.push_back(s_int);
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

  cnpy::npz_save(argv[2], "frames", frames.data(),
                 {frames.size() / config::N_RN16_FRAME, static_cast<size_t>(config::N_RN16_FRAME)}, "w");
  cnpy::npz_save(argv[2], "frames_dc", frames_dc.data(),
                 {frames_dc.size() / (config::N_T1 / 2), static_cast<size_t>(config::N_T1 / 2)}, "a");
  cnpy::npz_save(argv[2], "inter_est", inter_est.data(), {inter_est.size()}, "a");
  cnpy::npz_save(argv[2], "labels", frames_labels.data(),
                 {frames_labels.size() / config::N_RN16_FRAME, static_cast<size_t>(config::N_RN16_FRAME)}, "a");

  return 0;
}
