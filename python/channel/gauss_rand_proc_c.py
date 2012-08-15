from gnuradio import gr
from winelo.channel import spec2soc

class gauss_rand_proc_c(gr.hier_block2):
    def __init__(self, sample_rate, spec_type, method, N):
        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        model, spec_type = spec_type.split(':')

        if model == "cost207":
            from winelo.channel.cost207 import dopplerspecs
            doppler_spec = dopplerspecs(N = 201, fmax = 100, spec_type = spec_type)

        soc = spec2soc( doppler_spec.get_spec(), method = method, N = N )

        sources = []
        for freq, ampl, phase in soc.get_soc():
            #print "Creating a complex cosine with f=%f Hz and ampl=%f" % (freq, ampl)
            sources.append( gr.sig_source_c (sample_rate, gr.GR_COS_WAVE, freq, ampl) )

        adder = gr.add_cc()

        for idx, src in enumerate(sources):
            self.connect( src, ( adder, idx ) )

        self.connect(adder, self)
