from gnuradio import gr

from winelo.hw_models.generic_impairments.channel_interface import tx, rx
from winelo.hw_models.generic_impairments import awgn, gain, iq_imbalance, phase_noise


class basic_cc(gr.hier_block2):
    """ Mixing- and rate converting-only HW model.
    """
    def __init__(self, sim_bw, app_bw, center_f, sim_center_f, client_type,
                 f_offset=0.0, noise_ampl=0.0, gain_val=1.0, iq_mag=0.0,
                 iq_phase=0.0, alpha=0.0, phase_noise_mag=0.0):
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
        self.noise_ampl = noise_ampl
        self.gain = gain_val
        self.iq_mag = iq_mag
        self.iq_phase = iq_phase
        self.alpha = alpha
        self.phase_noise_mag = phase_noise_mag

        ##################################################
        # Blocks
        ##################################################
        self.awgn = awgn(self.noise_ampl)
        self.gain_blk = gain(self.gain)
        self.iq_imbal = iq_imbalance(self.iq_mag, self.iq_phase)
        self.phase_noise = phase_noise(self.alpha, self.phase_noise_mag)
        if client_type == "tx":
            self.channel_interface = tx(self.sim_bw, self.app_bw, self.f_shift,
                                        self.f_offset)
        else:
            self.channel_interface = rx(self.sim_bw, self.app_bw, self.f_shift,
                                        self.f_offset)

        ##################################################
        # Connections
        ##################################################
        if client_type == "tx":
            self.connect((self, 0), (self.phase_noise, 0))
            self.connect((self.phase_noise, 0), (self.iq_imbal, 0))
            self.connect((self.iq_imbal, 0), (self.channel_interface, 0))
            self.connect((self.channel_interface, 0), (self.gain_blk, 0))
            self.connect((self.gain_blk, 0), (self.awgn, 0))
            self.connect((self.awgn, 0), (self, 0))
        else:
            self.connect((self, 0), (self.awgn, 0))
            self.connect((self.awgn, 0), (self.gain_blk, 0))
            self.connect((self.gain_blk, 0), (self.channel_interface, 0))
            self.connect((self.channel_interface, 0), (self.iq_imbal, 0))
            self.connect((self.iq_imbal, 0), (self.phase_noise, 0))
            self.connect((self.phase_noise, 0), (self, 0))

    def set_center_freq(self, freq):
        """ Set new center frequency.
        """
        self.f_shift = freq + self.f_offset
        self.channel_interface.set_center_freq(freq)
