import numpy
from gnuradio import gr
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
from winelo.client import SendFactory
import time

class sim_sink_c(gr.block):

    def __init__(self, serverip, serverport, clientname,
                clientindex, packetsize, startreactor):
        gr.block.__init__(
            self,
            name = "WiNeLo sink",
            in_sig = [numpy.complex64],
            out_sig = [numpy.complex64],
        )
        print 'Instantiating %s' % clientname
        # counter that keeps track of the number of requested samples
        self.n_requested_samples = 0
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # to the profile
        # connect to the server
        reactor.connectTCP(serverip, serverport, SendFactory(self,
            {'type':'tx','name':clientname, 'index':clientindex,
            'packet_size':packetsize}))
        # start the reactor if the appropriate flag has been set.
        # THE REACTOR MUST NOT BE STARTED MORE THAN ONCE PER FLOWGRAPH
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
            n_requested_samples = self.n_requested_samples
            if n_requested_samples is 0:
                self.twisted_conn.condition.wait()
                #break
            elif n_requested_samples < len(input_items[0]):
                output_items[0] = input_items[0][0:n_requested_samples]
                break
            else:
                output_items[0] = input_items[0]
                break
        n_processed = len(output_items[0])
        self.n_requested_samples -= n_processed
        #self.twisted_conn.sendSamples(requested_samples)
        self.twisted_conn.condition.release()
        return n_processed

    def set_n_requested_samples(self, number_of_samples):
        self.n_requested_samples += number_of_samples

    def set_connection(self, twisted_conn):
        self.twisted_conn = twisted_conn
