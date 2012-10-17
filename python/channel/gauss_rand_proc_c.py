from gnuradio import gr

class gauss_rand_proc_c(gr.hier_block2):
    """ GNU radio block that models a complex Gaussian random process.
    """

    def __init__(self, sample_rate, spec_type, method, N, doppler_opts):
        """
        Parameters:

        sample_rate: int or float
            sample_rate of the flowgraph

        spec_type: string
            type of the spectrum. Must be something like cost207:jakes

        method: string
            method used to create the sum of sinusoids/cisoids

        N: int
            number of sinusoids/cisoids

        doppler_opts: Dictionary
            options for the Doppler spectrum

        """

        gr.hier_block2.__init__(self, "Complex Gaussian Random Process",
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.sample_rate = sample_rate
        self.method = method
        self.N = N

        self.model_type, self.spec_type = spec_type.split(':')
        self.model = self._get_model(doppler_opts)
        gauss_rand_proc_c = self._get_gauss_rand_proc_c()

        self.connect(gauss_rand_proc_c, self)

    def _get_model(self, doppler_opts):
        """ Returns the specified model for the Radio Channel.
        """
        if self.model_type == "cost207":
            import winelo.channel.models.cost207 as cost207
            try:
                opts_N = doppler_opts['N']
                opts_fmax = doppler_opts['fmax']
            except KeyError, e:
                print 'Key %s was not found in the doppler_opts dictionary.' % e.message
                print 'The COST 207 model requires the number of points at'
                print 'which the Doppler Spectrum is evaluated and the maximum'
                print 'Doppler shift. Try something like {\'N\':2001, \'fmax\':100}.'
            model = cost207.dopplerspecs(N = opts_N, fmax = opts_fmax)

        return model

    def _get_gauss_rand_proc_c(self):
        """ Returns the Gaussian random process.
        """
        spec_getter = getattr( self.model, 'get_' + self.spec_type)
        if self.spec_type in self.model.specs_odd:
            from winelo.channel import spec2soc
            soc = spec2soc( spec_getter(), method = self.method, N = self.N )
            sources = []
            adder = gr.add_cc()
            for idx, (freq, ampl) in enumerate(soc.get_soc()):
                sources.append( gr.sig_source_c (self.sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources[idx], ( adder, idx ) )
            return adder
        elif self.spec_type in self.model.specs_even:
            from winelo.channel import spec2sos
            # real part of the gaussian random process
            sos_real = spec2sos( spec_getter(), method = self.method, N = self.N )
            sources_real = []
            adder_real = gr.add_ff()
            for idx, (freq, ampl) in enumerate(sos_real.get_sos()):
                sources_real.append( gr.sig_source_f (self.sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources_real[idx], ( adder_real, idx ) )
            # imaginary part of the gaussian random process
            sos_imaginary = spec2sos( spec_getter(), method = self.method, N = self.N+1 )
            sources_imag = []
            adder_imag = gr.add_ff()
            for idx, (freq, ampl) in enumerate(sos_imaginary.get_sos()):
                sources_imag.append( gr.sig_source_f (self.sample_rate, gr.GR_COS_WAVE, freq, ampl) )
                self.connect( sources_imag[idx], ( adder_imag, idx ) )
            float2complex = gr.float_to_complex()
            self.connect(adder_real, (float2complex, 0))
            self.connect(adder_imag, (float2complex, 1))
            return float2complex
        else:
            print 'You picked a non-existant Doppler spectrum'
            print 'Pick one of the following: ',  model.specs_even + model.specs_odd
            return None

