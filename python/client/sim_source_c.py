import numpy
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import gr, uhd, blocks
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
import time

from winelo.client import SendFactory, uhd_gate


class sim_source_cc(gr.block):

    def __init__(self, serverip, serverport, clientname,
                 packetsize):
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
                                              'packet_size': packetsize})
                           )
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


class sim_source_c(gr.hier_block2, uhd_gate):
    """
    Wireless Netowrks In-the-Loop source

    Note: This is not a subclass of uhd.usrp_source because some methods
    shouldn't be available at all for this block.
    """
    def __init__(self, serverip, serverport, clientname,
                 packetsize, dataport, simulation, device_addr, stream_args):
        gr.hier_block2.__init__(self, "sim_source_c",
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        uhd_gate.__init__(self)

        self.simulation = simulation

        simsrc = sim_source_cc(serverip, serverport, clientname,
                               packetsize)
        if not self.simulation:
            self.usrp = uhd.usrp_source(device_addr, stream_args)  # TODO: Parameters

            self.connect(self.usrp, self)
        else:
            tcp_source = grc_blks2.tcp_source(itemsize=gr.sizeof_gr_complex,
                                              addr=serverip,
                                              port=dataport,
                                              server=False)

            self.gain_blk = blocks.multiply_const_vcc((1, ))

            self.connect(tcp_source, self.gain_blk, simsrc, self)
