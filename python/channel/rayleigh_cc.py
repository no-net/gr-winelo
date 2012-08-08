from gnuradio import gr
import winelo.channel

class rayleigh_cc(gr.hier_block2):
    def __init__(self, sample_rate=48000, N=10, dopplerspec='jakes'):
        gr.hier_block2.__init__(self, "Rayleigh",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        gauss_proc_real = winelo.channel.spec2sos(N, dopplerspec)
        # if the number of sinusoids does not differ the real part and the
        # imaginary part will be correlated. DO NOT WANT!
        gauss_proc_imag = winelo.channel.spec2sos(N+1, dopplerspec)

        real = winelo.channel.gauss_rand_proc_f(sample_rate, gauss_proc_real.get_sos())
        imag = winelo.channel.gauss_rand_proc_f(sample_rate, gauss_proc_imag.get_sos())

        complex_gauss = gr.float_to_complex()
        multi = gr.multiply_cc()

        self.connect( real, ( complex_gauss, 0 ) )
        self.connect( imag, ( complex_gauss, 1 ) )

        self.connect(complex_gauss, ( multi, 0 ) )
        self.connect(self, ( multi, 1) )

        self.connect(multi, self)
