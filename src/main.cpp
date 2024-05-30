#include <gnuradio/block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/top_block.h>

#include "rfid_block.hpp"

int main(int argc, char *argv[]) {
  gr::top_block_sptr tb = gr::make_top_block("main");
  auto source = gr::blocks::file_source::make(8, argv[1], false);
  auto my = rfid_block::make();
  tb->connect(source, 0, my, 0);
  tb->start();
  tb->wait();
  return 0;
}
