from gnuradio import gr


class none_cc(gr.hier_block2):
    """ No HW model.
    """
    def __init__(self, sim_bw, app_bw, center_f, sim_center_f, client_type):
        gr.hier_block2.__init__(
            self, "No HW model",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Blocks
        ##################################################
        self.multiply = gr.multiply_const_cc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.multiply, 0))
        self.connect((self.multiply, 0), (self, 0))

    def set_center_freq(self, freq):
        """ Set new center frequency.
        """
        print "[WARNING] WiNeLo - Center frequency adjustment not supported" \
              "by HW-model!"
