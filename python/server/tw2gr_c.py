import numpy

from gnuradio import gr
# import grextras for python blocks
import gnuradio.extras
from twisted.internet import reactor
import time

class tw2gr_c(gr.block):
    """ Interface from Twisted to GNU Radio.
    """

    def __init__(self, twisted_conn):
        gr.block.__init__(
            self,
            name = "winelo-tw2gr",
            in_sig = None,
            out_sig = [numpy.complex64],
        )
        self.samples = numpy.zeros(0)
        # the connection between this gr block and the corresponding twisted
        # conncetion
        self.twisted_conn = twisted_conn

    def work(self, input_items, output_items):
        self.twisted_conn.condition.acquire()
        while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
            samples = self.samples[:]
            if len(samples) is 0:
                self.twisted_conn.condition.wait()
                # check if the kill flag is set. If the flowgraph is torn down
                # this flag makes sure that the infinite loop can be exited
                if self.twisted_conn.kill is True:
                    self.twisted_conn.condition.release()
                    return 0
            elif len(samples) < len(output_items[0]):
                n_processed = len(samples)
                output_items[0][0:n_processed] = samples
                self.twisted_conn.condition.release()
                self.samples = self.samples[n_processed:]
                self.timeout_start = None
                return n_processed
            else:
                n_processed = len(output_items[0])
                output_items[0][:] = samples[0:n_processed]
                self.twisted_conn.condition.release()
                self.samples = self.samples[n_processed:]
                self.timeout_start = None
                return n_processed

    # called from twisted to add samples to the flowgraph
    def samples_received(self, samples):
        self.samples = numpy.append(self.samples, samples)
