from gnuradio import gr
import math


class iq_imbalance(gr.hier_block2):
    """
        IQ imbalance generator.

        Built from Matt Ettus's GRC file.
    """

    def __init__(self, magnitude=0, phase=0):
        """
            Parameters:

                amplitude: float
                phase: float (degree)
        """
        gr.hier_block2.__init__(
            self, "IQ Imbalance Generator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.magnitude = magnitude
        self.phase = phase

        ##################################################
        # Blocks
        ##################################################
        self.mag = gr.multiply_const_vff((math.pow(10, magnitude / 20.0), ))
        self.gr_multiply_const_vxx_0 = gr.multiply_const_vff(
            (math.sin(phase * math.pi / 180.0), ))
        self.gr_float_to_complex_0 = gr.float_to_complex(1)
        self.gr_complex_to_float_0 = gr.complex_to_float(1)
        self.gr_add_xx_0 = gr.add_vff(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.gr_float_to_complex_0, 0), (self, 0))
        self.connect((self, 0), (self.gr_complex_to_float_0, 0))
        self.connect((self.gr_complex_to_float_0, 0), (self.mag, 0))
        self.connect((self.mag, 0), (self.gr_float_to_complex_0, 0))
        self.connect((self.gr_add_xx_0, 0), (self.gr_float_to_complex_0, 1))
        self.connect((self.gr_multiply_const_vxx_0, 0), (self.gr_add_xx_0, 0))
        self.connect((self.gr_complex_to_float_0, 1), (self.gr_add_xx_0, 1))
        self.connect((self.gr_complex_to_float_0, 0),
                     (self.gr_multiply_const_vxx_0, 0))
