from gnuradio import gr, analog, blocks
from gnuradio import filter

import sys


class tx(gr.hier_block2):
    """
    Channel Interface.

    This block handles:
        - Rate up-conversion (app_bw to sim_bw).
        - Mixing.
        - Tx filtering.
    """
    def __init__(self, sim_bw, app_samp_rate, freq_shift, f_offset):
        """
        Parameters:

            sim_bw: float
            app_samp_rate: float
            freq_shift: float
        """
        gr.hier_block2.__init__(
            self, "Tx Channel Interface",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        interpolation = sim_bw / app_samp_rate

        if interpolation % 1 != 0.0:
            sys.exit("[ERROR] WiNeLo - Simulation bandwidth is not an "
                     "integer multiple of app sample rate: %s" % interpolation)
        else:
            print "[INFO] WiNeLo - Using Interpolation of %s for this node!" \
                  % int(interpolation)

        if app_samp_rate > sim_bw:
            sys.exit("[ERROR] WiNeLo - Simulation bandwidth too small!")

        self.interpolation = interpolation
        self.sim_bw = sim_bw
        self.app_samp_rate = app_samp_rate
        self.f_offset = f_offset
        self.freq_shift = freq_shift + f_offset

        ##################################################
        # Blocks
        ##################################################
        self.channel_filter = filter.pfb.interpolator_ccf(
            int(self.interpolation),
            (gr.firdes.low_pass_2(int(self.interpolation), self.sim_bw,
                                  self.app_samp_rate / 2,
                                  self.app_samp_rate / 10, 120,
                                  window=gr.firdes.WIN_BLACKMAN_hARRIS)))
        self.virt_lo = analog.sig_source_c(self.sim_bw, analog.GR_COS_WAVE,
                                           self.freq_shift, 1, 0)
        self.multiply = blocks.multiply_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect(self, self.channel_filter, (self.multiply, 0))
        self.connect(self.virt_lo, (self.multiply, 1))
        self.connect(self.multiply, self)

    def set_center_freq(self, freq):
        self.freq_shift = freq + self.f_offset
        self.virt_lo.set_frequency(self.freq_shift)


class rx(gr.hier_block2):
    """
    Channel Interface.

    This block handles:
        - Rate down-conversion (app_bw to sim_bw).
        - Mixing.
        - Rx filtering.
    """
    def __init__(self, sim_bw, app_samp_rate, freq_shift, f_offset):
        """
        Parameters:

            sim_bw: float
            app_samp_rate: float
            freq_shift: float
        """
        gr.hier_block2.__init__(
            self, "Rx Channel Interface",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        ##################################################
        # Parameters
        ##################################################
        decimation = sim_bw / app_samp_rate

        if decimation % 1 != 0.0:
            sys.exit("[ERROR] WiNeLo - Simulation bandwidth is not an "
                     "integer multiple of app sample rate: %s" % decimation)
        else:
            print "[INFO] WiNeLo - Using decimation of %s for this node!" \
                  % int(decimation)

        if app_samp_rate > sim_bw:
            sys.exit("[ERROR] WiNeLo - Simulation bandwidth too small!")

        self.decimation = decimation
        self.sim_bw = sim_bw
        self.app_samp_rate = app_samp_rate
        self.f_offset = f_offset
        self.freq_shift = freq_shift + f_offset

        ##################################################
        # Blocks
        ##################################################
        self.channel_filter = filter.freq_xlating_fir_filter_ccc(
            int(self.decimation),
            gr.firdes.low_pass_2(1, self.sim_bw, self.app_samp_rate / 2,
                                 self.app_samp_rate / 10, 120,
                                 window=gr.firdes.WIN_BLACKMAN_hARRIS),
            -self.freq_shift, self.sim_bw)

        ##################################################
        # Connections
        ##################################################
        self.connect(self, self.channel_filter)
        self.connect(self.channel_filter, self)

    def set_center_freq(self, freq):
        self.freq_shift = freq + self.f_offset
        self.channel_filter.set_center_freq(self.freq_shift)
