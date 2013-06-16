from gnuradio import gr


class phase_noise(gr.hier_block2):
    """
        Phase noise generator.

        Built from Matt Ettus's GRC file.
    """

    def __init__(self, alpha=0.1, noise_mag=0):
        """
            Parameters:

                alpha: float
                noise_mag: float
        """
        gr.hier_block2.__init__(
            self, "Phase Noise Generator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.alpha = alpha
        self.noise_mag = noise_mag

        ##################################################
        # Blocks
        ##################################################
        self.gr_transcendental_0_0 = gr.transcendental("sin", "float")
        self.gr_transcendental_0 = gr.transcendental("cos", "float")
        self.gr_single_pole_iir_filter_xx_0 = gr.single_pole_iir_filter_ff(
            alpha, 1)
        self.gr_noise_source_x_0 = gr.noise_source_f(gr.GR_GAUSSIAN, noise_mag,
                                                     42)
        self.gr_multiply_xx_0 = gr.multiply_vcc(1)
        self.gr_float_to_complex_0 = gr.float_to_complex(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.gr_float_to_complex_0, 0),
                     (self.gr_multiply_xx_0, 1))
        self.connect((self.gr_noise_source_x_0, 0),
                     (self.gr_single_pole_iir_filter_xx_0, 0))
        self.connect((self.gr_multiply_xx_0, 0), (self, 0))
        self.connect((self, 0), (self.gr_multiply_xx_0, 0))
        self.connect((self.gr_single_pole_iir_filter_xx_0, 0),
                     (self.gr_transcendental_0, 0))
        self.connect((self.gr_single_pole_iir_filter_xx_0, 0),
                     (self.gr_transcendental_0_0, 0))
        self.connect((self.gr_transcendental_0, 0),
                     (self.gr_float_to_complex_0, 0))
        self.connect((self.gr_transcendental_0_0, 0),
                     (self.gr_float_to_complex_0, 1))
