import numpy
from gnuradio import gr
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
from winelo.client import SendFactory
import time

class sim_source_c(gr.block):

    def __init__(self, serverip, serverport, clientname,
                clientindex, packetsize, startreactor):
        gr.block.__init__(
            self,
            name = "WINELO-Simulation Source",
            in_sig = None,
            out_sig = [numpy.complex64],
        )
        print 'Instantiating %s' % clientname
        # this will store all samples that came from twisted
        self.samples = numpy.zeros(0)
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # connect to the server
        reactor.connectTCP(serverip, serverport, SendFactory(self,
            {'type':'rx','name':clientname, 'index':clientindex,
            'packet_size':packetsize}))
        if startreactor:
            print 'Starting the reactor'
            print 'Please make sure that no other WINELO Sink is instantiated '\
                  'after the reactor has been started'
            thread.start_new_thread(reactor.run, () ,{'installSignalHandlers':0})
        print 'giving twisted time to setup and block everything'
        time.sleep(1)

    def work(self, input_items, output_items):
        self.twisted_conn.condition.acquire()
        while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
            samples = self.samples[:]
            if len(samples) is 0:
                self.twisted_conn.condition.wait()
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

    def new_samples_received(self, samples):
        self.samples = numpy.append(self.samples, samples)

    def set_connection(self, connection):
        self.twisted_conn = connection
