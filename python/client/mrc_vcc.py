import numpy

#from gnuradio import blks2
from gnuradio import gr
#import gnuradio.extras


class mrc_vcc(gr.basic_block):
    def __init__(self, pilot_seq_len, channel_coherence_len, num_inputs):
        gr.basic_block.__init__(
            self,
            name="Maximum Ratio Combining",
            in_sig=num_inputs * [(numpy.complex64, channel_coherence_len)],
            out_sig=[(numpy.complex64, channel_coherence_len - pilot_seq_len)],
        )
        # length of the pilot sequence
        self.pilot_seq_len = pilot_seq_len
        # for how many samples the channel can be  assumed to be constant
        self.channel_coherence_len = channel_coherence_len
        self.outlen = channel_coherence_len - pilot_seq_len
        # number of input streams
        self.num_inputs = num_inputs

    def general_work(self, input_items, output_items):
        min_input_vecs = min([x.shape[0] for x in input_items])
        min_output_vecs = min([x.shape[0] for x in output_items])
        min_number_vecs = min(min_input_vecs, min_output_vecs)

        if min_number_vecs is 0:
            self.consume_each(0)
            return 0
        k = 0
        while k < min_number_vecs:
            channel_est_total = 0
            out = numpy.zeros((1, self.outlen))
            for in_stream in input_items:
                in_data = in_stream[k]
         #       print in_data
                channel_est = sum(in_data[0:self.pilot_seq_len]) / float(self.pilot_seq_len)
                channel_est_total += abs(channel_est ** 2)
                out = out + numpy.conj(channel_est) * in_data[self.pilot_seq_len:]
            # Take the average over all input stream.
            # The input streams were already weighted by their corresponding
            # channel coefficients.
            out = out / abs(channel_est_total)
        #    print 'output_items.shape', output_items[0].shape
            output_items[0][k][:] = out
            k += 1
        self.consume_each(min_number_vecs)
        return min_number_vecs
