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

class qa_evm_cc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        src_data0 = (1,2,3,1,1)+(2,2,2,2,2)
        src_data1 = (1,1,2,4,0)+(0,0,0,0,0)
        expected_result = (12./5, 4)
        src0 = gr.vector_source_c(src_data0)
        src1 = gr.vector_source_c(src_data1)
        evm = winelo_swig.evm_cc(win_size = 5)
        sink = gr.vector_sink_f()
        # set up fg
        self.tb.connect(src0, (evm, 0))
        self.tb.connect(src1, (evm, 1))
        self.tb.connect(evm, sink)
        self.tb.run ()
        # check data
        result_data = sink.data ()
        print result_data
        self.assertFloatTuplesAlmostEqual (expected_result, result_data, 6)
        # check data


if __name__ == '__main__':
    gr_unittest.main ()
