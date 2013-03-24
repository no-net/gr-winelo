#!/usr/bin/env python
#
# Copyright 2012 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
#

from gnuradio import gr, gr_unittest
import winelo_swig

class qa_mpc_channel_cc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001 (self):
        src_data = (1,2,3,4,5)
        src_gauss_ch1 = (2,2,1,1,2)
        expected_result = (2,4,3,4,10)
        src0 = gr.vector_source_c(src_data)
        src1 = gr.vector_source_c(src_gauss_ch1)
        mpc_channel = winelo_swig.mpc_channel_cc((0,), (1,))
        sink = gr.vector_sink_c()
        # set up fg
        self.tb.connect(src0, (mpc_channel, 0))
        self.tb.connect(src1, (mpc_channel, 1))
        self.tb.connect(mpc_channel, sink)
        self.tb.run ()
        # check data
        result_data = sink.data ()
        self.assertFloatTuplesAlmostEqual (expected_result, result_data, 6)

    def test_002 (self):
        src_data = (1,0,0,0,0)
        src_gauss_ch1 = (1,1,1,1,1)
        src_gauss_ch2 = (1,1,1,1,1)
        expected_result = (1,0,0,0.707106781,0)
        src0 = gr.vector_source_c(src_data)
        src1 = gr.vector_source_c(src_gauss_ch1)
        src2 = gr.vector_source_c(src_gauss_ch2)
        mpc_channel = winelo_swig.mpc_channel_cc((0,3), (1,0.5))
        sink = gr.vector_sink_c()
        # set up fg
        self.tb.connect(src0, (mpc_channel, 0))
        self.tb.connect(src1, (mpc_channel, 1))
        self.tb.connect(src2, (mpc_channel, 2))
        self.tb.connect(mpc_channel, sink)
        self.tb.run ()
        # check data
        result_data = sink.data ()
        self.assertFloatTuplesAlmostEqual (expected_result, result_data, 6)


if __name__ == '__main__':
    gr_unittest.main ()
