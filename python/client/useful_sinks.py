#!/usr/bin/env python

from gnuradio import gr
# import grextras for python blocks
import gnuradio.extras

import numpy
import time


class compare_2streams_sink_c(gr.block):
    def __init__(self):
        gr.block.__init__(
            self,
            name="Print complex samples sink",
            in_sig=[numpy.complex64, numpy.complex64],
            out_sig=None,
        )
        self.sample_counter = 0
        self.sample_error_counter = 0
        self.timestart = time.clock()

    def work(self, input_items, output_items):
        num_input_items = len(input_items[0])
        i = 0
        while i < num_input_items:
            self.sample_counter += 1
            if numpy.abs(input_items[0][i] - input_items[1][i]) > 0.01:
                self.sample_error_counter += 1
            i += 1
        print 'After %f seconds and %d samples the sample-error-rate is %f' % (
            time.clock() - self.timestart,
            self.sample_counter,
            self.sample_error_counter / float(self.sample_counter))
        return num_input_items
