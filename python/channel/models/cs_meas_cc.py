from gnuradio import gr
from winelo import mpc_channel_cc
import pickle

class cs_meas_cc(gr.hier_block2):
    """ A GNU Radio block that uses a channel sounder measurement for modelling
    a channel.
    """
    def __init__(self, sample_rate, filename):
        """
        Parameters:

        sample_rate: int or float
            sample_rate of the flowgraph

        filename: string
            file containing the channel model

        
        Notes:
            The modelfile was created with the pickle module and contains a list
            of sum of cisoids, each sum of cisoids models the Doppler spectrum
            with a specific delay. If one list element is empty this means that
            there exist no scatterers with the specified delay. Each sum of
            cisoids, i.e. list element, contains again a list of amplitudes and
            frequencies.

        """

        gr.hier_block2.__init__(self, "Channel Sounder Measurement",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.sample_rate = sample_rate
        fp = open(filename, 'r')

        model = pickle.load(fp)
    
        self.taps_delays = []
        # check for non-empty list elements to find multipath components with a
        # certain delay
        for idx, mpc in enumerate(model):
            if mpc:
               self.taps_delays.append(idx)

        # print 'taps_delays', self.taps_delays
        # create a tapped delay line structure, since the amplitudes of the sum
        # of cisoids already contain all the information about the power of a
        # Doppler spectrum, the power delay profile is set to 1 for all delays.
        self.mpc_channel = mpc_channel_cc(self.taps_delays, [1]*len(self.taps_delays))

        # loop through all delays
        for idx, delay in enumerate(self.taps_delays):
            adder = gr.add_cc() 
            # loop through all cisoids of a delay
            for iidx, (freq, ampl) in enumerate(model[delay]):
                src = gr.sig_source_c(sample_rate, gr.GR_COS_WAVE, freq, ampl)
                self.connect(src, (adder, iidx))
            # print iidx
            self.connect(adder, (self.mpc_channel, idx+1))

        self.connect(self,       (self.mpc_channel, 0))
        self.connect(self.mpc_channel, self)
