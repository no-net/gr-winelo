from gnuradio import gr

from winelo.hw_models.generic_impairments.channel_interface import tx, rx


class mixing_only_cc(gr.hier_block2):
    """ Mixing- and rate converting-only HW model.
    """
    def __init__(self, net_id, sim_bw, app_bw, center_f, sim_center_f, client_type,
                 f_offset=0.0):
        gr.hier_block2.__init__(
            self, "Mixing-only HW model",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        self.sim_bw = sim_bw
        self.app_bw = app_bw
        self.f_shift = center_f - sim_center_f
        self.f_offset = f_offset

        ##################################################
        # Blocks
        ##################################################
        if client_type == "tx":
            self.channel_interface = tx(self.sim_bw, self.app_bw, self.f_shift,
                                        self.f_offset)
        else:
            self.channel_interface = rx(self.sim_bw, self.app_bw, self.f_shift,
                                        self.f_offset)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.channel_interface, 0))
        self.connect((self.channel_interface, 0), (self, 0))

    def set_center_freq(self, freq):
        """ Set new center frequency.
        """
        self.f_shift = freq + self.f_offset
        self.channel_interface.set_center_freq(freq)
