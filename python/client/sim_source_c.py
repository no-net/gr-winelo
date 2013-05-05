import numpy
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import gr, uhd, blocks, analog
from gruel import pmt
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
from threading import Thread
import time

from winelo.client import SendFactory, uhd_gate
from winelo.client.tcp_blocks import tcp_source


class sim_source_cc(gr.block):

    def __init__(self, serverip, serverport, clientname,
                 packetsize):
        gr.block.__init__(
            self,
            name="WiNeLo source",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        print '[INFO] WiNeLo - Instantiating %s' % clientname
        # this will store all samples that came from twisted
        self.samples = numpy.zeros(0)
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # Needed for WiNeLo-time
        self.virtual_counter = 0
        self.samp_rate = 1000000  # TODO: Get from GRC
        # Port used by tcp source/sink for sample transmission
        self.dataport = None
        self.samples_to_produce = 0
        self.p_size = 4096
        # connect to the server
        reactor.connectTCP(serverip,
                           serverport,
                           SendFactory(self, {'type': 'rx',
                                              'name': clientname,
                                              'packet_size': packetsize})
                           )
        if not reactor.running:
            print '[INFO] WiNeLo - Starting the reactor'
            #thread.start_new_thread(reactor.run, (), {'installSignalHandlers': 0})
            Thread(target=reactor.run, args=(False,)).start()
        else:
            time.sleep(3)
        print '[INFO] WiNeLo - giving twisted time to setup and block everything'
        time.sleep(3)

    def work(self, input_items, output_items):
        #print "Source work called"
        self.twisted_conn.condition.acquire()
        if self.virtual_counter == 0:
            self.generate_rx_tags()
        while True:
            # this is necessary because twisted and gnuradio are running in
            # different threads. So it is possible that new samples arrive
            # while gnuradio is still working on the old samples
            if len(input_items[0]) is 0:
                #print "DEBUG: sim_source - waiting for items"
                self.twisted_conn.condition.wait()
                #print "DEBUG: sim_source - got items"
                #if len(input_items[0]) is 0:
                #    return 0
            #if self.samples_to_produce <= len(input_items[0]) and self.samples_to_produce > 0:
            #    produce_n_samples = self.samples_to_produce
            #else:
            #    produce_n_samples = len(input_items[0])

            elif self.samples_to_produce < len(input_items[0]):
                #print "DEBUG: samples to produce:", samples_to_produce, " - len input:", len(input_items[0])
                output_items[0] = input_items[0][0:self.samples_to_produce]
            else:
                output_items[0] = input_items[0]

            #elif len(input_items[0]) < len(output_items[0]):
            #    n_processed = len(input_items[0])
            #    output_items[0] = input_items[0]
                #print "Source processed:", n_processed
                #print "DEBUG: sim_source - elif - items processed:", n_processed
                #time.sleep(1.0 / self.samp_rate * n_processed)
            #else:
            #    n_processed = len(output_items[0])
            #    output_items[0] = input_items[0][0:n_processed]
                #print "Source processed:", n_processed
                #print "DEBUG: sim_source - else - items processed:", n_processed
                #time.sleep(1.0 / self.samp_rate * n_processed)
            self.timeout_start = None
            n_processed = len(output_items[0])
            self.virtual_counter += n_processed
            #if n_processed < self.p_size:
            #    print "DEBUG: source - ACK less samples"
            self.samples_to_produce -= n_processed
            if self.samples_to_produce == 0:
                #print "DEBUG: ACK sent"
                self.twisted_conn.samplesReceived()
                self.samples_to_produce = self.p_size
            self.twisted_conn.condition.release()
            return n_processed

    def new_samples_received(self, samples):
        self.samples = numpy.append(self.samples, samples)

    def set_connection(self, connection):
        self.twisted_conn = connection

    def set_dataport(self, port):
        self.dataport = port
        print '[INFO] WiNeLo - Port %s will be used for data transmission' % self.dataport

    def get_dataport(self):
        while self.dataport is None:
            reactor.callWhenRunning(time.sleep, 0.5)
        return self.dataport

    def get_time_now(self):
        # Calculate time according tot the sample rate & the number of processed items
        time = 1.0 / self.samp_rate * self.virtual_counter
        full_secs = int(time)
        frac_secs = time - int(time)
        # Return full & fractional seconds (like UHD)
        return full_secs, frac_secs

    def generate_rx_tags(self):
        #Produce tags
        offset = self.nitems_written(0) + 0
        key_time = pmt.pmt_string_to_symbol("rx_time")
        #value_time = pmt.from_python(1.0 / self.samp_rate * self.virtual_counter)
        value_time = pmt.from_python(self.get_time_now())

        key_rate = pmt.pmt_string_to_symbol("rx_rate")
        value_rate = pmt.from_python(self.samp_rate)

        self.add_item_tag(0, offset, key_time, value_time)
        self.add_item_tag(0, offset, key_rate, value_rate)


class sim_source_c(gr.hier_block2, uhd_gate):
    """
    Wireless Netowrks In-the-Loop source

    Note: This is not a subclass of uhd.usrp_source because some methods
    shouldn't be available at all for this block.
    """
    def __init__(self, serverip, serverport, clientname,
                 packetsize, simulation, device_addr, stream_args):
        gr.hier_block2.__init__(self, "sim_source_c",
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        uhd_gate.__init__(self)
        self.simulation = simulation
        self.serverip = serverip
        if not self.simulation:
            self.usrp = uhd.usrp_source(device_addr, stream_args)  # TODO: Parameters
            self.connect(self.usrp, self)
        else:
            self.simsrc = sim_source_cc(serverip, serverport, clientname,
                                        packetsize)
            # TODO: dirty hack!!!
            #self.tcp_source = grc_blks2.tcp_source(itemsize=gr.sizeof_gr_complex,
            #                                       addr=self.serverip,
            #                                       port=self.simsrc.get_dataport(),
            #                                       server=False)
            self.tcp_source = gr.udp_source(itemsize=gr.sizeof_gr_complex,
                                            host=self.serverip,
                                            port=self.simsrc.get_dataport())
            self.gain_blk = blocks.multiply_const_vcc((1, ))
            self.connect(self.tcp_source, self.gain_blk, self.simsrc, self)
