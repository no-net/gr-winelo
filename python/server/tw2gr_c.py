import numpy

from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2
# import grextras for python blocks
import gnuradio.extras


class tw2gr_cc(gr.block):
    """ Interface from Twisted to GNU Radio.
    """

    def __init__(self, twisted_conn):
        gr.block.__init__(
            self,
            name="winelo-tw2gr",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        # the connection between this gr block and the corresponding twisted
        # conncetion
        self.twisted_conn = twisted_conn

    def work(self, input_items, output_items):
        #self.twisted_conn.condition.acquire()
        while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
            if len(input_items[0]) is 0:
                # check if the kill flag is set. If the flowgraph is torn down
                # this flag makes sure that the infinite loop can be exited
                if self.twisted_conn.kill is True:
                    return 0
            elif len(input_items[0]) < len(output_items[0]):
                n_processed = len(input_items[0])
                output_items[0][0:n_processed] = input_items[0][0:n_processed]
                self.timeout_start = None
                self.twisted_conn.sampled_passed_2_gr = True
                return n_processed
            else:
                n_processed = len(output_items[0])
                output_items[0][:] = input_items[0][0:n_processed]
                self.timeout_start = None
                self.twisted_conn.sampled_passed_2_gr = True
                return n_processed


class tw2gr_c(gr.hier_block2):
    """
    Connects a TCP sink to gr2tw_c.
    """
    def __init__(self, twisted_con, tcp_addr, tcp_port):
        gr.hier_block2.__init__(self, "tw2gr_c",
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        tw2gr = tw2gr_cc(twisted_con)
        tcp_source = grc_blks2.tcp_source(itemsize=gr.sizeof_gr_complex,
                                          addr=tcp_addr,
                                          port=tcp_port,
                                          server=True)
        print "Connecting tw2gr..."
        self.connect(tcp_source, tw2gr, self)
