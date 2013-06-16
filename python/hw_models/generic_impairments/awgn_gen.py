from gnuradio import gr


class awgn(gr.hier_block2):
    """ White Gaussian Noise Adder.
    """

    def __init__(self, noise_ampl=0):
        """
            Parameters:

                noise_ampl: float
        """
        gr.hier_block2.__init__(
            self, "Additive White Gaussian Noise Generator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.noise_ampl = noise_ampl

        ##################################################
        # Blocks
        ##################################################
        self.gr_noise_source_x_0 = gr.noise_source_c(gr.GR_GAUSSIAN,
                                                     noise_ampl, 42)
        self.gr_add_xx_0 = gr.add_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.gr_add_xx_0, 0))
        self.connect((self.gr_noise_source_x_0, 0), (self.gr_add_xx_0, 1))
        self.connect((self.gr_add_xx_0, 0), (self, 0))
