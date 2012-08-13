from gnuradio import gr

class gauss_rand_proc_c(gr.hier_block2):
    def __init__(self, sample_rate, spectrum):
        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        sources = []
        for freq, ampl in spectrum:
            #print "Creating a complex cosine with f=%f Hz and ampl=%f" % (freq, ampl)
            sources.append( gr.sig_source_c (sample_rate, gr.GR_COS_WAVE, freq, ampl) )

        adder = gr.add_cc()

        for idx, src in enumerate(sources):
            self.connect( src, ( adder, idx ) )

        self.connect(adder, self)
