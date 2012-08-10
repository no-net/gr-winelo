#!/usr/bin/env python

from gnuradio import gr

import numpy
import time

class count_samples_cc(gr.block):
    def __init__(self):
        gr.block.__init__(
            self,
            name = "count all samples",
            in_sig = [numpy.complex64],
            out_sig = [numpy.complex64],
        )
        self.counter = 0
        self.timestart = time.time()

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        #process data
        out[:] = in0
        delta = len(in0)
        if delta > 0:
            self.counter += delta
            elapsed = time.time() - self.timestart
            print 'Rate: %f samples/sec' % (delta/elapsed)
            print 'So far %i samples have passed this block' % self.counter
            self.timestart = time.time()
        return len(out)
