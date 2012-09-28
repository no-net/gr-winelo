from gnuradio import gr
from winelo.channel.gauss_rand_proc_c import gauss_rand_proc_c

class rayleigh_cc(gr.hier_block2):
    def __init__(self, sample_rate, fmax):
        gr.hier_block2.__init__(self, "Rayleigh Channel",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        self.sample_rate = sample_rate
        self.channel_opts = {'N':2001, 'fmax': fmax}
        self.rayleigh = gauss_rand_proc_c(self.sample_rate, "cost207:jakes", "mea", 12, self.channel_opts)
        self.multiply = gr.multiply_cc()

        self.connect(self,          (self.multiply, 0))
        self.connect(self.rayleigh, (self.multiply, 1))
        self.connect(self.multiply, self)
