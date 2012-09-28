from gnuradio import gr
from winelo import mpc_channel_cc
from winelo.channel import gauss_rand_proc_c

class paths_4(gr.hier_block2):
    def __init__(self, sample_rate, fmax):
        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.sample_rate = sample_rate
        # Statistics of this channel, taken from
        # "Mobile Radio Channels", Paetzold, 2011, p 357
        # Delays of the multipath components in seconds
        delays = [0, 0.2e-6, 0.4e-6, 0.6e-6]
        print 'delays', delays
        # Delays expressed in samples
        self.taps_delays = [ int(sample_rate*delay) for delay in delays ]
        print 'delays in samples', self.taps_delays
        # power delay profile
        self.pdp = [1, 0.63, 0.1, 0.01]
        # channel options
        self.channel_opts = {'N':2001, 'fmax': fmax}
        self.mpc_channel = mpc_channel_cc(self.taps_delays, self.pdp)
        # The different multipath components have to be uncorrelated. This is
        # the reason for choosing changing values for N
        self.mpc1 = gauss_rand_proc_c(sample_rate, "cost207:rice", "gmea", 14, self.channel_opts)
        self.mpc2 = gauss_rand_proc_c(sample_rate, "cost207:jakes", "mea", 12, self.channel_opts)
        self.mpc3 = gauss_rand_proc_c(sample_rate, "cost207:jakes", "mea", 10, self.channel_opts)
        self.mpc4 = gauss_rand_proc_c(sample_rate, "cost207:jakes", "mea", 8, self.channel_opts)

        self.connect(self,      (self.mpc_channel, 0))
        self.connect(self.mpc1, (self.mpc_channel, 1))
        self.connect(self.mpc2, (self.mpc_channel, 2))
        self.connect(self.mpc3, (self.mpc_channel, 3))
        self.connect(self.mpc4, (self.mpc_channel, 4))
        self.connect(self.mpc_channel, self)
