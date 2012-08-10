import numpy
from gnuradio import gr

import struct
from twisted.internet import reactor

class gr2tw_c(gr.block):

    def __init__(self, twisted_conn):
        gr.block.__init__(
            self,
            name = "WINELO-Simulation Sink",
            in_sig = [numpy.complex64],
            out_sig = None,
        )
        self.twisted_conn = twisted_conn

    def work(self, input_items, output_items):
        packet_size = self.twisted_conn.factory.packet_size
        # if the number of input_items is larger than the packet_size, send a
        # packet to the receivers. Otherwise don't do anything
        if len( input_items[0] ) >= packet_size:
            samples = input_items[0][0:packet_size]
            sendstring = [struct.pack('=f', el.real) + struct.pack('=f', el.imag) for el in samples]
            sendstring = "".join(sendstring)
            self.twisted_conn.ack_received = False
            reactor.callFromThread( self.twisted_conn.transport.write, 'dataEOH%sEOP' % sendstring)
            return packet_size
        else:
            return 0
