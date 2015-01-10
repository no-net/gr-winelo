#!/usr/bin/env python

from gnuradio import gr
# import grextras for python blocks
#import gnuradio.extras

import numpy
import time


class count_samples_cc(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="count all samples",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        self.limit = 1e6
        self.counter = 0
        self.delta = 0
        self.timestart = time.time()

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        #process data
        out[:] = in0
        self.delta = self.delta + len(in0)
        if self.delta > self.limit:
            self.counter += self.delta
            elapsed = time.time() - self.timestart
            print 'Rate: %f samples/sec' % (self.delta / elapsed)
            print 'So far %i samples have passed this block' % self.counter
            self.timestart = time.time()
            self.delta = 0
        return len(out)
