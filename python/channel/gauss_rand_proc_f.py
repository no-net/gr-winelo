from gnuradio import gr

class gauss_rand_proc_f(gr.hier_block2):
    def __init__(self, sample_rate, spectrum):
        gr.hier_block2.__init__(self, "Float Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_float))


        sources = []
        for freq, ampl in spectrum:
            sources.append( gr.sig_source_f (sample_rate, gr.GR_COS_WAVE, freq, ampl) )

        adder = gr.add_ff()

        for idx, src in enumerate(sources):
            self.connect( src, ( adder, idx ) )

        self.connect(adder, self)
