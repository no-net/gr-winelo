from gnuradio import gr
from winelo.channel import spec2soc

class gauss_rand_proc_c(gr.hier_block2):
    def __init__(self, sample_rate, spec_type, method, N, doppler_opts):
        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        model, spec_type = spec_type.split(':')

        if model == "cost207":
            from winelo.channel.cost207 import dopplerspecs
            try:
                opts_N = doppler_opts['N']
                opts_fmax = doppler_opts['fmax']
            except KeyError, e:
                print 'Key %s was not found in the doppler_opts dictionary.' % e.message
                print 'The COST 207 model requires the number of points at'
                print 'which the Doppler Spectrum is evaluated and the maximum'
                print 'Doppler shift. Try something like {\'N\':201, \'fmax\':100}.'
            doppler_spec = dopplerspecs(N = opts_N, fmax = opts_fmax, spec_type = spec_type)

        soc = spec2soc( doppler_spec.get_spec(), method = method, N = N )

        sources = []
        for freq, ampl, phase in soc.get_soc():
            #print "Creating a complex cosine with f=%f Hz and ampl=%f" % (freq, ampl)
            sources.append( gr.sig_source_c (sample_rate, gr.GR_COS_WAVE, freq, ampl) )

        adder = gr.add_cc()

        for idx, src in enumerate(sources):
            self.connect( src, ( adder, idx ) )

        self.connect(adder, self)
