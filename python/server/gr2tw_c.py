import numpy
from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2
# import grextras for python blocks
import gnuradio.extras

import struct
from twisted.internet import reactor


class gr2tw_cc(gr.block):
    """ Interface from GNU Radio to Twisted.
    """

    def __init__(self, twisted_conn):
        gr.block.__init__(
            self,
            name="WINELO-Simulation Sink",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        self.twisted_conn = twisted_conn

    def work(self, input_items, output_items):
        packet_size = self.twisted_conn.factory.packet_size
        # if the number of input_items is larger than the packet_size, send a
        # packet to the receivers. Otherwise don't do anything
        if len(input_items[0]) >= packet_size:
            #self.twisted_conn.handleAck(packet_size)
            output_items[0] = input_items[0][0:packet_size]
            return packet_size
        else:
            return 0


class gr2tw_c(gr.hier_block2):
    """
    Connects a TCP sink to gr2tw_c.
    """
    def __init__(self, twisted_con, tcp_addr, tcp_port):
        gr.hier_block2.__init__(self, "gr2tw_c",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                gr.io_signature(0, 0, 0))

        gr2tw = gr2tw_cc(twisted_con)
        tcp_sink = grc_blks2.tcp_sink(itemsize=gr.sizeof_gr_complex,
                                      addr=tcp_addr,
                                      port=tcp_port,
                                      server=True)

        self.connect(self, gr2tw, tcp_sink)
