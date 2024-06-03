#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Query RFID
# Author: Yachen Mao
# GNU Radio version: 3.10.10.0

from command_gen import reader_cmd_gen
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time




class rfid_query(gr.top_block):

    def __init__(self, duration=0.1, freq=900e6, out='rx.cf32', rx_gain=0, tag_filter='all', tx_gain=20):
        gr.top_block.__init__(self, "Query RFID", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.duration = duration
        self.freq = freq
        self.out = out
        self.rx_gain = rx_gain
        self.tag_filter = tag_filter
        self.tx_gain = tx_gain

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2e6

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_subdev_spec('B:0', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_auto_dc_offset(False, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.blocks_vector_source_x_0 = blocks.vector_source_c(reader_cmd_gen(samp_rate, tag_filter), True, 1, [])
        self.blocks_head_0_0 = blocks.head(gr.sizeof_gr_complex*1, (int(samp_rate * (duration + 0.2))))
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, (int(samp_rate * duration)))
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, out, False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_head_0_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_head_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_head_0, 0))


    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration
        self.blocks_head_0.set_length((int(self.samp_rate * self.duration)))
        self.blocks_head_0_0.set_length((int(self.samp_rate * (self.duration + 0.2))))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_sink_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)

    def get_out(self):
        return self.out

    def set_out(self, out):
        self.out = out
        self.blocks_file_sink_0.open(self.out)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 1)

    def get_tag_filter(self):
        return self.tag_filter

    def set_tag_filter(self, tag_filter):
        self.tag_filter = tag_filter
        self.blocks_vector_source_x_0.set_data(reader_cmd_gen(self.samp_rate, self.tag_filter), [])

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_head_0.set_length((int(self.samp_rate * self.duration)))
        self.blocks_head_0_0.set_length((int(self.samp_rate * (self.duration + 0.2))))
        self.blocks_vector_source_x_0.set_data(reader_cmd_gen(self.samp_rate, self.tag_filter), [])
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--duration", dest="duration", type=eng_float, default=eng_notation.num_to_str(float(0.1)),
        help="Set Duration [default=%(default)r]")
    parser.add_argument(
        "--freq", dest="freq", type=eng_float, default=eng_notation.num_to_str(float(900e6)),
        help="Set Frequency [default=%(default)r]")
    parser.add_argument(
        "--out", dest="out", type=str, default='rx.cf32',
        help="Set Output Name [default=%(default)r]")
    parser.add_argument(
        "--rx-gain", dest="rx_gain", type=intx, default=0,
        help="Set Rx Gain [default=%(default)r]")
    parser.add_argument(
        "-f", "--tag-filter", dest="tag_filter", type=str, default='all',
        help="Set Filter [default=%(default)r]")
    parser.add_argument(
        "--tx-gain", dest="tx_gain", type=intx, default=20,
        help="Set Tx Gain [default=%(default)r]")
    return parser


def main(top_block_cls=rfid_query, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(duration=options.duration, freq=options.freq, out=options.out, rx_gain=options.rx_gain, tag_filter=options.tag_filter, tx_gain=options.tx_gain)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
