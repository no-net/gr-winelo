#
# Copyright 1980-2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

#import numpy
#from numpy import np
#from math import pi
from gnuradio import gr
import pmt
#from gnuradio.digital import packet_utils
#import gnuradio.digital as gr_digital
import gnuradio.extras  # brings in gr.block
#import Queue
import time


# /////////////////////////////////////////////////////////////////////////////
#               Heart Beat - period blob generation with param key and value
# /////////////////////////////////////////////////////////////////////////////

class heart_beat(gr.block):
    """
    Generates blob at specified interval (w/ sleep)

    This block was taken from the gr-easymac/pre-cog package.
    """
    def __init__(self, period, key, value):
        """
        The input is a pmt message blob.
        Non-blob messages will be ignored.
        The output is a byte stream for the modulator

        @param period: Time between blopbs
        @param key: String for key
        @param value: String for value
        """
        # TODO: Problem here -> instance of heart_beat
        gr.block.__init__(
            self,
            name="simple_mac",
            in_sig=None,
            out_sig=None,
            has_msg_input=False,
            num_msg_outputs=1,
        )

        #self.mgr = pmt.mgr()
        #for i in range(64):
        #    self.mgr.set(pmt.make_blob(10000))
        self.period = period
        self.key = key
        self.value = value
        self.counter = 0
        self.counter_treshold = 63

    def work(self, input_items, output_items):

        #print "DEBUG: Heartbeat work called!"
        #while(self.counter < self.counter_treshold):
        while(1):
            #print "DEBUG: Heartbeat - new run, run no %s" % self.counter
            #blob = self.mgr.acquire(True) #block
            #pmt.blob_resize(blob, len(self.value))
            #pmt.blob_rw_data(blob)[:] = \
                #numpy.fromstring(self.value,dtype="uint8")
            self.post_msg(0, pmt.string_to_symbol(self.key),
                          pmt.string_to_symbol(self.value))  # blob)
            #self.post_msg(0, pmt.string_to_symbol(self.key), blob)
            time.sleep(self.period)
            #self.counter += 1
        #self.counter = 0
        #print "DEBUG: Heartbeat work finished!"
        #return 0
