import numpy
#from grc_gnuradio import blks2 as grc_blks2
from gnuradio import gr, uhd, blocks  # , analog
import pmt
# import grextras for python blocks
#import gnuradio.extras

from twisted.internet import reactor
#import thread
from threading import Thread
import time
import random

from winelo.client import SendFactory, uhd_gate
#from winelo.client.tcp_blocks import tcp_source


class sim_source_cc(gr.sync_block):

    def __init__(self, hier_blk, serverip, serverport, clientname,
                 packetsize, samp_rate, center_freq, net_id=0):
        gr.sync_block.__init__(
            self,
            name="WiNeLo source",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
        )
        print '[INFO] WiNeLo - Instantiating %s' % clientname
        self.hier_blk = hier_blk
        # this will store all samples that came from twisted
        self.samples = numpy.zeros(0)
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        self.net_id = net_id
        # Needed for WiNeLo-time
        self.virtual_counter = 0
        # Evaluated for timed commands -> can be higher/absolute (GPS time)
        self.virtual_time = 0
        self.virt_offset = 0
        self.absolute_time = True
        self.samp_rate = samp_rate
        # Port used by tcp source/sink for sample transmission
        self.dataport = None
        self.packet_size = packetsize
        self.samples_to_produce = self.packet_size
        self.drop_one_in_n_cmds = 0  # TODO: was 50 for per_measurement!
        # TODO: DEBUG
        #self.no_zero_counter = 0
        self.dbg_counter = 0
        # connect to the server
        reactor.connectTCP(serverip,
                           serverport,
                           SendFactory(self, {'type': 'rx',
                                              'name': clientname,
                                              'centerfreq': center_freq,
                                              'samprate': self.samp_rate,
                                              'net_id': self.net_id,
                                              'packet_size': packetsize})
                           )
        if not reactor.running:
            print '[INFO] WiNeLo - Starting the reactor'
            #thread.start_new_thread(reactor.run, (),
                                     #{'installSignalHandlers': 0})
            Thread(target=reactor.run, args=(False,)).start()
        else:
            time.sleep(2)
        print '[INFO] WiNeLo - giving twisted time to setup and block ' \
              'everything'
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
            if self.samples_to_produce <= len(input_items[0]) and \
                    self.samples_to_produce > 0:
                produce_n_samples = self.samples_to_produce
            else:
                produce_n_samples = len(input_items[0])

            if produce_n_samples > len(output_items[0]):
                produce_n_samples = len(output_items[0])

            #print "DEBUG: src - produce_n: %s - samples_to_produce: %s" \
                #% (produce_n_samples, self.samples_to_produce)

            #elif self.samples_to_produce < len(input_items[0]):
            #    print "DEBUG: samples to produce:", self.samples_to_produce,"\
                #" - len input:", len(input_items[0]), " - len output:", \
                #len(output_items[0])
            #    if self.samples_to_produce > 0:
            #        output_items[0][:] = \
                #input_items[0][0:self.samples_to_produce]
            #else:
            output_items[0][0:produce_n_samples] = \
                input_items[0][0:produce_n_samples]

            ### DEBUG:
            #no_zeros_last = self.no_zero_counter
            #for item in output_items[0][0:produce_n_samples]:
            #    if item != 0:
            #        self.no_zero_counter += 1
            #if self.no_zero_counter != no_zeros_last:
            #    print "self.no_zero_counter", self.no_zero_counter

            #elif len(input_items[0]) < len(output_items[0]):
            #    n_processed = len(input_items[0])
            #    output_items[0] = input_items[0]
                #print "Source processed:", n_processed
                #print "DEBUG: sim_source - elif - items processed:",
                    #n_processed
                #time.sleep(1.0 / self.samp_rate * n_processed)
            #else:
            #    n_processed = len(output_items[0])
            #    output_items[0] = input_items[0][0:n_processed]
                #print "Source processed:", n_processed
                #print "DEBUG: sim_source - else - items processed:", \
                    #n_processed
                #time.sleep(1.0 / self.samp_rate * n_processed)
            self.timeout_start = None
            self.virtual_counter += produce_n_samples
            self.virtual_time += produce_n_samples / float(self.samp_rate)
            # TODO TODO: Produce max. diff samples, then call commands before
            # running again!
            # CHECK TIMED COMMANDS
            if len(self.hier_blk.commands) > 0 and \
                    len(self.hier_blk.command_times) > 0:
                #print "DEBUG: evaluating cmd times"
                cmd_time, n_cmds = self.hier_blk.command_times[0]
                #print "DEBUG: time %s - n_cmds %s - virt_time %s" \
                    #% (time, n_cmds, self.virtual_time)
                while self.virtual_time > (cmd_time + 0.0065):
                    #print "DEBUG: calling run_timed_cmds"
                    if self.drop_one_in_n_cmds > 0:
                        rand_no = random.randint(1, self.drop_one_in_n_cmds)
                    else:
                        rand_no = 0
                    if rand_no == 1:
                        self.hier_blk.command_times.pop(0)
                        self.hier_blk.commands.pop(0)
                        print "[INFO] WiNeLo - Dropped cmd due to HW model!"
                    else:
                        #print "DEBUG: RxRxRx - Tuning cmd sent at: %s - " \
                               #"CMD time: %s" % (self.virtual_time, cmd_time)
                        #print "DEBUG: Set RX-freq to %s at %s" \
                            #% (self.hier_blk.commands[0][1], cmd_time)
                        #print "DEBUG: virtual counter:", self.virtual_counter
                        self.hier_blk.command_times.pop(0)
                        #print "DEBUG---------------------hier_blk_cmd_times",\
                            #self.hier_blk.command_times
                        self.run_timed_cmds(n_cmds)
                    if len(self.hier_blk.command_times) > 0:
                        #print "DEBUG: NEW TIME, CMDS"
                        cmd_time, n_cmds = self.hier_blk.command_times[0]
                    else:
                        break
            #if produce_n_samples < self.p_size:
            #    print "DEBUG: source - ACK less samples"
            self.samples_to_produce -= produce_n_samples
            #print "DEBUG: NO ACK sent"
            #print "DEBUG: NO ACK - produced:", len(output_items[0])
            #print "DEBUG: NO ACK - samples to produce:", \
                   #self.samples_to_produce
            #print "DEBUG: NO ACK - len input", len(input_items[0])
            if self.samples_to_produce == 0:
                self.dbg_counter += 1
                #print "DEBUG: ACK senti no:", self.dbg_counter
                #print "DEBUG: ACK - produced:", produce_n_samples
                self.twisted_conn.samplesReceived()
                self.samples_to_produce = self.packet_size
            self.twisted_conn.condition.release()
            #print "DEBUG: sim_src - produced:", n_processed
            return produce_n_samples

    def run_timed_cmds(self, n_cmds):
        for i in range(n_cmds):
            cmd, args = self.hier_blk.commands.pop()
            #print "DEBUG: src - running cmd %s with args %s" % (cmd, args)
            cmd(*args)

    def new_samples_received(self, samples):
        self.samples = numpy.append(self.samples, samples)

    def set_connection(self, connection):
        self.twisted_conn = connection

    def set_dataport(self, port):
        self.dataport = port
        print '[INFO] WiNeLo - Port %s will be used for data transmission' \
              % self.dataport

    def set_packetsize(self, packet_size):
        self.packet_size = packet_size
        if self.samples_to_produce > self.packet_size:
            self.samples_to_produce = self.packet_size

    def update_virttime(self, time_offset):
        if self.absolute_time:
            print "[INFO] WiNeLo - Setting source time to server time:", \
                  time_offset
            self.virtual_time += time_offset
            self.virt_offset = time_offset

    def get_dataport(self):
        while self.dataport is None:
            reactor.callWhenRunning(time.sleep, 0.5)
        return self.dataport

    def get_time_now(self):
        # Calculate time according tot the sample rate & the number of
        # processed items
        #time = 1.0 / self.samp_rate * self.virtual_counter
        time = self.virtual_time
        full_secs = int(time)
        frac_secs = time - int(time)
        # Return full & fractional seconds (like UHD)
        return full_secs, frac_secs

    def generate_rx_tags(self):
        #Produce tags
        offset = self.nitems_written(0) + 0
        key_time = pmt.string_to_symbol("rx_time")
        #value_time = pmt.from_python(1.0 /
                                      #self.samp_rate * self.virtual_counter)
        value_time = pmt.to_pmt(self.get_time_now())

        key_rate = pmt.string_to_symbol("rx_rate")
        value_rate = pmt.to_pmt(self.samp_rate)

        self.add_item_tag(0, offset, key_time, value_time)
        self.add_item_tag(0, offset, key_rate, value_rate)


class sim_source_c(gr.hier_block2, uhd_gate):
    """
    Wireless Netowrks In-the-Loop source

    Note: This is not a subclass of uhd.usrp_source because some methods
    shouldn't be available at all for this block.
    """
    def __init__(self, serverip, serverport, clientname, packetsize,
                 simulation, samp_rate, center_freq, net_id,
                 device_addr, stream_args):
        gr.hier_block2.__init__(self, "sim_source_c",
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        uhd_gate.__init__(self)
        self.simulation = simulation
        self.serverip = serverip
        self.samp_rate = samp_rate
        self.typ = 'rx'
        if not self.simulation:
            self.usrp = uhd.usrp_source(device_addr, stream_args)
                # TODO: Parameters
            self.connect(self.usrp, self)
        else:
            self.simsrc = sim_source_cc(self, serverip, serverport, clientname,
                                        packetsize, samp_rate, center_freq,
                                        net_id)
            # TODO: dirty hack!!!
#            self.tcp_source = grc_blks2.tcp_source(itemsize=gr.sizeof_gr_complex,
#                                                   addr=self.serverip,
#                                                   port=self.simsrc.get_dataport(),
#                                                   server=False)
            self.tcp_source = blocks.udp_source(itemsize=gr.sizeof_gr_complex,
                                            host=self.serverip,
                                            port=self.simsrc.get_dataport(),
                                            payload_size=1472,
                                            eof=False)  #,
#                                            wait=True)
            self.gain_blk = blocks.multiply_const_vcc((1, ))
            self.connect(self.tcp_source, self.gain_blk, self.simsrc, self)
