from gnuradio import gr


class const_cc(gr.hier_block2):
    """ Constant channel model.
    """
    def __init__(self, tx_id, rx_id, k):
        gr.hier_block2.__init__(
            self, "No HW model",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.k = k

        ##################################################
        # Blocks
        ##################################################
        self.multiply = gr.multiply_const_cc(self.k)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.multiply, 0))
        self.connect((self.multiply, 0), (self, 0))
