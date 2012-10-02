from gnuradio import gr
from winelo import mpc_channel_cc
import pickle

class cs_meas_cc(gr.hier_block2):
    def __init__(self, sample_rate):
        gr.hier_block2.__init__(self, "Channel Sounder Measurement",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.sample_rate = sample_rate
        filename = '/home/baier/gritloop/channel_sounder/gr-channelsounder/apps/cost207_mod.pickle'
        fp = open(filename, 'r')

        model = pickle.load(fp)


        self.taps_delays = []
        for idx, mpc in enumerate(model):
            if mpc:
               self.taps_delays.append(idx)

        print 'taps_delays', self.taps_delays
        self.mpc_channel = mpc_channel_cc(self.taps_delays, [1]*len(self.taps_delays))

        for idx, delay in enumerate(self.taps_delays):
            adder = gr.add_cc()
            for iidx, (freq, ampl) in enumerate(model[delay]):
                src = gr.sig_source_c(sample_rate, gr.GR_COS_WAVE, freq, ampl)
                self.connect(src, (adder, iidx))
            self.connect(adder, (self.mpc_channel, idx+1))

        self.connect(self,       (self.mpc_channel, 0))
        self.connect(self.mpc_channel, self)
