from gnuradio import gr


class gain(gr.hier_block2):
    """ Gain block.
    """

    def __init__(self, gain):
        """
            Parameters:

                gain: gr_complex
        """
        gr.hier_block2.__init__(
            self, "No HW model",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.gain = gain

        ##################################################
        # Blocks
        ##################################################
        self.multiply = gr.multiply_const_cc(self.gain)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.multiply, 0))
        self.connect((self.multiply, 0), (self, 0))

    def set_gain(self, gain):
        """ Set gain.
        """
        self.gain = gain
        self.multiply.set_k(gain)
