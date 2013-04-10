import numpy
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import gr, uhd, blocks
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
import time

from winelo.client import SendFactory, uhd_gate


class sim_sink_cc(gr.block):

    def __init__(self, serverip, serverport, clientname,
                 packetsize):
        gr.block.__init__(
            self,
            name="WiNeLo sink",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        print 'Instantiating %s' % clientname
        # counter that keeps track of the number of requested samples
        self.n_requested_samples = 0
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # Port used by tcp source/sink for sample transmission
        self.dataport = None
        # to the profile
        # connect to the server
        reactor.connectTCP(serverip,
                           serverport,
                           SendFactory(self, {'type': 'tx',
                                              'name': clientname,
                                              'packet_size': packetsize})
                           )
        # THE REACTOR MUST NOT BE STARTED MORE THAN ONCE PER FLOWGRAPH
        if not reactor.running:
            print 'Starting the reactor'
            print 'Please make sure that no other WINELO Sink is instantiated '\
                  'after the reactor has been started'
            thread.start_new_thread(reactor.run, (), {'installSignalHandlers': 0})
        else:
            time.sleep(2)
        print 'giving twisted time to setup and block everything'
        time.sleep(1)

    def work(self, input_items, output_items):
        self.twisted_conn.condition.acquire()
        while True:
            n_requested_samples = self.n_requested_samples
            if n_requested_samples is 0:
                self.twisted_conn.condition.wait()
            elif n_requested_samples < len(input_items[0]):
                output_items[0] = input_items[0][0:n_requested_samples]
                break
            else:
                output_items[0] = input_items[0]
                break
        n_processed = len(output_items[0])
        self.n_requested_samples -= n_processed
        self.twisted_conn.condition.release()
        return n_processed

    def set_n_requested_samples(self, number_of_samples):
        self.n_requested_samples += number_of_samples

    def set_connection(self, twisted_conn):
        self.twisted_conn = twisted_conn

    def set_dataport(self, port):
        self.dataport = port
        print "Port %s will be used for data transmission to/from the server" % self.dataport

    def get_dataport(self):
        while self.dataport is None:
            time.sleep(0.2)
        return self.dataport


class sim_sink_c(gr.hier_block2, uhd_gate):
    """
    Hier block used for managing the WiNeLo-stuff.

    Connects a TCP sink to sim_source_cc.
    """
    def __init__(self, serverip, serverport, clientname,
                 packetsize, simulation, device_addr, stream_args):
        gr.hier_block2.__init__(self, "sim_source_c",
                                gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                gr.io_signature(0, 0, 0))
        uhd_gate.__init__(self)
        self.simulation = simulation
        if not self.simulation:
            self.usrp = uhd.usrp_sink(device_addr, stream_args)  # TODO: Parameters
            self.connect(self, self.usrp)
        else:
            simsnk = sim_sink_cc(serverip, serverport, clientname,
                                 packetsize)
            tcp_sink = grc_blks2.tcp_sink(itemsize=gr.sizeof_gr_complex,
                                          addr=serverip,
                                          port=simsnk.get_dataport(),
                                          server=False)
            self.gain_blk = blocks.multiply_const_vcc((1, ))
            self.connect(self, self.gain_blk, simsnk, tcp_sink)
