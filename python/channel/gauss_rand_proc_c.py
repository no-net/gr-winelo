from gnuradio import gr


class gauss_rand_proc_c(gr.hier_block2):
    def __init__(self, sample_rate, spec_type, method, N, doppler_opts):
        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.model_type, self.spec_type = spec_type.split(':')
        self.model = self.get_model()



        self.connect(adder, self)

    def get_model(self):
        if self.model_type == "cost207":
            import winelo.channel.cost207 as cost207
            try:
                opts_N = doppler_opts['N']
                opts_fmax = doppler_opts['fmax']
            except KeyError, e:
                print 'Key %s was not found in the doppler_opts dictionary.' % e.message
                print 'The COST 207 model requires the number of points at'
                print 'which the Doppler Spectrum is evaluated and the maximum'
                print 'Doppler shift. Try something like {\'N\':201, \'fmax\':100}.'
            model = cost207.dopplerspecs(N = opts_N, fmax = opts_fmax)

        return model

    def get_gauss_rand_proc_c(self):
        spec_getter = getattr( self.model, 'get_' + self.spec_type)
        if self.spec_type in model.specs_odd:
            from winelo.channel import spec2soc
            soc = spec2soc( spec_getter(), method = self.method, N = self.N )
            sources = []
            adder = gr.add_cc()
            for idx, (freq, ampl) in enumerate(soc.get_soc()):
                sources.append( gr.sig_source_c (sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources[idx], ( adder, idx ) )
            return adder
        elif self.spec_type in model.specs_even:
            from winelo.channel import spec2soc
            # real part of the gaussian random process
            sos_real = spec2sos( spec_getter(), method = self.method, N = self.N )
            sources_real = []
            adder_real = gr.add_ff()
            for idx, (freq, ampl) in enumerate(sos_real.get_sos()):
                sources_real.append( gr.sig_source_f (sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources[idx], ( adder, idx ) )
            # imaginary part of the gaussian random process
            sos_imaginary = spec2sos( spec_getter(), method = self.method, N = self.N )
            sources_imaginary = []
            adder_imaginary = gr.add_ff()
            for idx, (freq, ampl) in enumerate(sos_imaginary.get_sos()):
                sources_imaginary.append( gr.sig_source_f (sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources[idx], ( adder, idx ) )
            float2complex = gr.float_to_complex()
            self.connect(adder_real, (float2complex, 0))
            self.connect(adder_imag, (float2complex, 0))
            return float2complex
        else:
            print 'You picked a non-existant Doppler spectrum'
            print 'Pick one of the following: ',  model.specs_even + model.specs_odd
            return None

