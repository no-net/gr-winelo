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
            name="WiNeLo source",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        print 'Instantiating %s' % clientname
        # this will store all samples that came from twisted
        self.samples = numpy.zeros(0)
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # connect to the server
        reactor.connectTCP(serverip,
                           serverport,
                           SendFactory(self, {'type': 'rx',
                                              'name': clientname,
                                              'index': clientindex,
                                              'packet_size': packetsize})
                           )
        if startreactor:
            print 'Starting the reactor'
            print 'Please make sure that no other WINELO Sink is instantiated '\
                  'after the reactor has been started'
            thread.start_new_thread(reactor.run, (), {'installSignalHandlers': 0})
        print 'giving twisted time to setup and block everything'
        time.sleep(1)

    def work(self, input_items, output_items):
        self.twisted_conn.condition.acquire()
        while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
            if len(input_items[0]) is 0:
                self.twisted_conn.condition.wait()
                #pass
            elif len(input_items[0]) < len(output_items[0]):
                n_processed = len(input_items[0])
                output_items[0][0:n_processed] = input_items[0][0:n_processed]
                #self.twisted_conn.transport.write('ackEOHdummyEOP')
                self.twisted_conn.samplesReceived()
                self.twisted_conn.condition.release()
                #self.twisted_conn.transport.write('ackEOHdummyEOP')
                self.timeout_start = None
                return n_processed
            else:
                n_processed = len(output_items[0])
                output_items[0][:] = input_items[0][0:n_processed]
                #self.twisted_conn.transport.write('ackEOHdummyEOP')
                self.twisted_conn.samplesReceived()
                self.twisted_conn.condition.release()
                self.timeout_start = None
                return n_processed

    def new_samples_received(self, samples):
        self.samples = numpy.append(self.samples, samples)

    def set_connection(self, connection):
        self.twisted_conn = connection
