import numpy

from gnuradio import gr  # , blocks
#from grc_gnuradio import blks2 as grc_blks2
# import grextras for python blocks
#import gnuradio.extras
#from winelo.client.tcp_blocks import tcp_source


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
        self.dbg_samp_count = 0

    def work(self, input_items, output_items):
        #print "DEBUG: tw2gr - work called"
        #print "INPUT:", input_items[0]
        #self.twisted_conn.condition.acquire()
        if self.twisted_conn.kill is True:
            #self.twisted_conn.condition.release()
            #print "DEBUG: tw2gr - work done --> killed!"
            return 0
        #while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
#            if len(input_items[0]) is 0:
#                print "DEBUG: tw2gr - no input items!"
#                # check if the kill flag is set. If the flowgraph is torn down
#                self.twisted_conn.condition.wait()
#                # this flag makes sure that the infinite loop can be exited
#                if self.twisted_conn.kill is True:
#                    print "DEBUG: TW2GR received kill signal"
#                    self.twisted_conn.condition.release()
#                    return 0
        if len(input_items[0]) < len(output_items[0]):
            n_processed = len(input_items[0])
            #print "DEBUG: tw2gr - elif - items processed:", n_processed
        else:
            n_processed = len(output_items[0])
            #output_items[0][0:n_processed] = input_items[0][0:n_processed]
            #self.twisted_conn.condition.release()
            #self.timeout_start = None
            #self.twisted_conn.sampled_passed_2_gr = True
            #print "DEBUG: tw2gr - else - items processed:", n_processed

        output_items[0][0:n_processed] = input_items[0][0:n_processed]
        #self.twisted_conn.condition.release()
        self.timeout_start = None
        self.twisted_conn.sampled_passed_2_gr = True

        self.dbg_samp_count += n_processed
        #print "DEBUG: tw2gr - produced_items:", self.dbg_samp_count
        #print output_items[0]
        return n_processed


class tw2gr_c(gr.hier_block2):
    """
    Connects a TCP sink to gr2tw_c.
    """
    def __init__(self, twisted_con, tcp_addr, tcp_port, app_center_freq,
                 app_samp_rate, sim_bw, sim_center_freq):
        gr.hier_block2.__init__(self, "tw2gr_c",
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        self.tw2gr = tw2gr_cc(twisted_con)
#        self.tcp_source = tcp_source(itemsize=gr.sizeof_gr_complex,
#                                     addr=tcp_addr,
#                                     port=tcp_port,
#                                     server=True)
        self.tcp_source = gr.udp_source(itemsize=gr.sizeof_gr_complex,
                                        host=str(tcp_addr),
                                        port=tcp_port,
                                        payload_size=1472,
                                        eof=False,
                                        wait=True)

        print "Connecting tw2gr..."
        self.connect(self.tcp_source, self.tw2gr, self)
