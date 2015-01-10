import numpy
from gnuradio import gr
#from grc_gnuradio import blks2 as grc_blks2
# import grextras for python blocks
#import gnuradio.extras
#from winelo.client.tcp_blocks import tcp_sink


class gr2tw_cc(gr.basic_block):
    """ Interface from GNU Radio to Twisted.
    """

    def __init__(self, twisted_conn, tcp_port):
        gr.basic_block.__init__(
            self,
            name="winelo-gr2tw",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        self.twisted_conn = twisted_conn
        self.port = tcp_port

    def work(self, input_items, output_items):
        #print "DEBUG: gr2tw - Input:", input_items[0]
        packet_size = self.twisted_conn.factory.packet_size
        # if the number of input_items is larger than the packet_size, send a
        # packet to the receivers. Otherwise don't do anything
        if len(input_items[0]) >= packet_size:
            n_processed = packet_size
            #print "packet-size:", packet_size
            #print "DEBUG GR2TW full - port:", self.port
            #print "DEBUG: gr2tw - packet sent"
            #print "DEBUG: gr2tw - len out: %s " % len(output_items[0])
            #print "DEBUG: gr2tw - len in: %s " % len(input_items[0])
        elif len(input_items[0]) > 0:
            #print "DEBUG GR2TW part - port:", self.port
            #print "DEBUG: gr2tw - NO packet sent - len input_items:", \
                #len(input_items[0])
            n_processed = len(input_items[0])
            #output_items[0] = packet_size * [0]
            #return len(input_items[0])
        else:
            print "DEBUG: gr2tw - no input_items to produce out_items"
            return 0

        if n_processed > len(output_items[0]):
            n_processed = len(output_items[0])

        output_items[0][0:n_processed] = input_items[0][0:n_processed]
        return n_processed


class gr2tw_c(gr.hier_block2):
    """
    Connects a TCP sink to gr2tw_c.
    """
    def __init__(self, twisted_con, tcp_addr, tcp_port, app_center_freq,
                 app_samp_rate, sim_bw, sim_center_freq):
        gr.hier_block2.__init__(self, "gr2tw_c",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                gr.io_signature(0, 0, 0))
        gr2tw = gr2tw_cc(twisted_con, tcp_port)
#        self.tcp_sink = tcp_sink(itemsize=gr.sizeof_gr_complex,
#                                 addr=tcp_addr,
#                                 port=tcp_port,
#                                 server=True)
        self.tcp_sink = gr.udp_sink(itemsize=gr.sizeof_gr_complex,
                                    host=tcp_addr,
                                    port=tcp_port,
                                    payload_size=1472,
                                    eof=False)

        self.connect(self, gr2tw, self.tcp_sink)
