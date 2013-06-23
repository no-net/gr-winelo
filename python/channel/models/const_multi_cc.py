from gnuradio import gr


class const_multi_cc(gr.hier_block2):
    """ Constant channel model.
    """
    def __init__(self, tx_id, rx_id,
                 k11=0.0, k12=1.0, k13=1.0,
                 k21=1.0, k22=0.0, k23=1.0,
                 k31=1.0, k32=1.0, k33=0.0):
        gr.hier_block2.__init__(
            self, "No HW model",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        # Use Symmetric channels for this model
        #k21 = k12
        #k31 = k13
        #k32 = k23
        # No self-coupling
        #k11 = k22 = k33 = 0
        # Build the channel matrix
        self.k = [[k11, k12, k13],
                  [k21, k22, k23],
                  [k31, k32, k33]]

        ##################################################
        # Blocks
        ##################################################
        self.multiply = gr.multiply_const_cc(self.k[tx_id - 1][rx_id - 1])
        print "[INFO] WiNeLo - Channel model: Setting k = %s for clients %s "\
              "and %s" % (self.k[tx_id - 1][rx_id - 1], tx_id, rx_id)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.multiply, 0))
        self.connect((self.multiply, 0), (self, 0))
