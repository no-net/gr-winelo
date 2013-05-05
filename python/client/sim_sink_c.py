import numpy
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import gr, uhd, blocks
from gruel import pmt
# import grextras for python blocks
import gnuradio.extras

from twisted.internet import reactor
import thread
from threading import Thread
import time
import precog

from winelo.client import SendFactory, uhd_gate
from winelo.client.tcp_blocks import tcp_sink
from winelo import heart_beat


class sim_sink_cc(gr.basic_block):

    def __init__(self, serverip, serverport, clientname,
                 packetsize):
        gr.basic_block.__init__(
            self,
            name="WiNeLo sink",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64],
            num_msg_inputs=1,
            num_msg_outputs=0,
        )
        print '[INFO] WiNeLo - Instantiating %s' % clientname
        # counter that keeps track of the number of requested samples
        self.n_requested_samples = 0
        # this is used to connect the block to the twisted reactor
        self.twisted_conn = None
        # Port used by tcp source/sink for sample transmission
        self.dataport = None
        # Zero-padding stuff
        self.tags = {'tx_time': [],
                     'tx_sob': [],
                     'tx_eob': []
                     }
        self.zeros_to_produce = 0
        self.produce_zeros = False
        self.produce_zeros_next = False
        self.samples_to_tx = 0
        self.next_tx_time = 0
        self.last_eob = 0
        self.samp_rate = 1000000  # TODO: Get sampp_rate from GRC!!!!!!!

        self.no_input_counter = 0
        self.max_no_input = 20
        self.got_sob_eob = False
        #self.got_sob = False
        self.last_sob_offset = 0
        # Virtual USRP register
        self.virtual_counter = 0
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
            print '[INFO] WiNeLo - Starting the reactor'
            #thread.start_new_thread(reactor.run, (), {'installSignalHandlers': 0})
            Thread(target=reactor.run, args=(False,)).start()
        else:
            time.sleep(1)
        print '[INFO] WiNeLo - giving twisted time to setup and block everything'
        time.sleep(1)

   # def forecast(self, noutput_items, ninput_items_required):
   #     ninput_items_required[0] = noutput_items

    def general_work(self, input_items, output_items):
        #if len(input_items[0]) == 0:
        #    return -1
        dbg_late = False
        self.twisted_conn.condition.acquire()
       # print "Sim_sink Work called"
        #print "DEBUG: len input:", len(input_items[0])

        #if not (self.produce_zeros or self.produce_zeros_next):
        if self.samples_to_tx == 0 and not (self.produce_zeros or self.produce_zeros_next):
            self.tags = {'tx_time': [],
                        'tx_sob': [],
                        'tx_eob': []
                        }
            self.evaluate_timestamps(self.nitems_read(0), len(input_items[0]))
            #print "DEBUG: Evaluating timestamps..."
            #print "---- samples_to_tx:", self.samples_to_tx
            #print "zeros_to_produce:", self.zeros_to_produce

        if self.produce_zeros_next:
            self.produce_zeros = True
            self.produce_zeros_next = False

        # Stop zero-padding
        #print self.zeros_to_produce
        if self.produce_zeros and (self.zeros_to_produce == 0):
            self.produce_zeros = False
            print "DEBUG: Stopped zero-padding"

        # Get no. zeros to produce
        dhg_late = False
        if len(self.tags['tx_time']) >= 1:
            self.next_tx_time = self.tags['tx_time'].pop(0)
            #print "TX time:", self.next_tx_time, " - last eob:", self.last_eob
            #print "DEBUG: Zeros_to_produce before:", self.zeros_to_produce
            print "[INFO] WiNeLo - Zeros to produce:", (self.next_tx_time - self.last_eob)
            print "DEBUG: Zeros to  produce", self.zeros_to_produce
            self.zeros_to_produce += (self.next_tx_time - self.last_eob)
            #self.got_sob = True
            if self.zeros_to_produce < 0:
                print '[ERROR] WiNeLo - Got SOB-tag too late. produced too much Zeros! Try increasing the realtime multiplicator!'
                print 'DEBUG: produce_zeros:', self.produce_zeros
                print 'DEBUG: produce_zeros_nxt:', self.produce_zeros_next
                #self.virtual_counter = self.next_tx_time
                self.zeros_to_produce = 0
                dbg_late = True
        #elif len(self.tags['tx_time']) > 1:
            #print "ERROR: Too much tx_time-TAGs in work-call!"
            #time.sleep(30)

        # Switch back to non-padding
        if len(self.tags['tx_sob']) >= 1 and not self.produce_zeros_next:
            self.last_sob_offset = self.tags['tx_sob'].pop(0)
            input_items[0] = input_items[0][self.last_sob_offset:]
            self.got_sob_eob = True
        #elif len(self.tags['tx_sob']) > 1:
            #print "ERROR: Too much tx_sob-TAGs in work-call!"
            #time.sleep(30)

        # Start zero-padding
        if len(self.tags['tx_eob']) >= 1:
            #print "DEBUG: self.tags tx_eob", self.tags['tx_eob']
            #print "Start padding of ", self.zeros_to_produce, " zeros"
            eob_offset = self.tags['tx_eob'].pop(0)  # TODO: Check if offset-1 or offset!
            #print "DEBUG: self.samples_to_tx = ", eob_offset, " - ", self.last_sob_offset
            self.samples_to_tx = eob_offset - self.last_sob_offset + 1
            input_items[0] = input_items[0][0:self.samples_to_tx]
            #print "DEBUG: Switching to zero-padding mode"
            #dhg_late = True
            self.produce_zeros_next = True
            #dbg_late = True
            #self.zeros_to_produce = -1
            # TODO TODO TODO: virtual_counter statt next_tx_time! (wichtig bei
            # GPS time z.b.
            self.last_eob = self.next_tx_time + self.samples_to_tx # TODO: check +-1!
            #print "DEBUG: calculated last_eob:", self.virtual_counter, " + ", self.zeros_to_produce, " + ", samples_to_tx
            self.got_sob_eob = True
        #elif len(self.tags['tx_eob']) > 1:
            #print "ERROR: Too much tx_eob-TAGs in work-call!"
            #time.sleep(30)

        if dbg_late:
            #print "DEBUG: Don't switch to zero=padding mode"
            self.produce_zeros_next = False

        #print "DEBUG: sink - work"
        while True:
            #print "DEBUG: sink - work -while-loop"
            n_requested_samples = self.n_requested_samples
            # TODO: Check packet-size
            if self.n_requested_samples > 4096:
                # Produce max packetsize samples
                n_requested_samples = 4096
            if n_requested_samples is 0:
                # Wait for samples
                dbg = "if"
                #print "DEBUG: sim_sink waiting for request!"
                self.twisted_conn.condition.wait()
                #print "DEBUG: sim_sink - request received"
                #if n_requested_samples is 0:
                #    return 0
                #self.n_requested_samples = 4096  # TODO: packetsize!
            # TODO: evtl. drop packets while zero-padding!

            elif self.produce_zeros:
                # We have to insert zeros
                #print "DEBUG: elif1"
                dbg = "elif1"
                #print "DEBUG: Producing Zeros..."
                #print "DEBUG: Requested Samples", n_requested_samples
                #Don't go over 0!
                if (self.zeros_to_produce > 0) and (self.zeros_to_produce - n_requested_samples) < 0:
                    # Stop zero-padding!
                    output_items[0] = self.zeros_to_produce * [0]
                else:
                    output_items[0] = n_requested_samples * [0]
                self.zeros_to_produce -= len(output_items[0])
                #print "DEBUG: produced zeros:", len(output_items[0])
                # TODO TODO: Multiplicator, realtime-mode!
                time.sleep(1.0 / self.samp_rate * len(output_items[0]))
                self.consume(0, 0)
                #n_processed = 0
                #self.n_requested_samples -= len(output_items[0])
                #self.virtual_counter += len(output_items[0])
                break

            #elif (n_requested_samples < len(input_items[0])) and (n_requested_samples > 0):
                #print "DEBUG: elif1, req samp:", n_requested_samples
                #output_items[0] = input_items[0][0:n_requested_samples]
                #self.consume(0, len(output_items[0]))
                #n_processed = len(output_items[0])
                #break

            # TODO TODO TODO TODO TODO: Fass diese zwei schleifen zusammen, es
            # duerfen max samples_to_tx und auch max n_req ausgegeben werden!

            elif len(input_items[0]) > 0 and not self.produce_zeros_next and (n_requested_samples > 0):
                # Move samples from the input to the output
                #print "DEBUG: else - req samples:", n_requested_samples
                #print "DEBUG: elif2"
                dbg = "elif2"
                if self.samples_to_tx <= n_requested_samples and self.samples_to_tx > 0:
                    samples_to_produce = self.samples_to_tx
                else:
                    samples_to_produce = n_requested_samples

                if samples_to_produce < len(input_items[0]):
                    #print "DEBUG: samples to produce:", samples_to_produce, " - len input:", len(input_items[0])
                    output_items[0] = input_items[0][0:samples_to_produce]
                else:
                    output_items[0] = input_items[0]
                    self.got_sob = False
                self.consume(0, len(output_items[0]))
                if self.samples_to_tx > 0:
                    self.samples_to_tx -= len(output_items[0])
                # TODO: Produce maximum samples_to_tx output items!!!
                print "DEBUG: Consumed", len(output_items[0]), "items."
                #self.consume(0, len(output_items[0]))
                #n_processed = len(output_items[0])
                break
            #elif not self.got_sob_eob:
            #elif not self.got_sob:
            else:
                # Get the simulation running if no input_items are available
                # and we didn't get an eob/sob tag
                dbg = "elif3"
                # Needed to start the simulation
                #self.no_input_counter += 1
                #if self.no_input_counter == self.max_no_input:
                #self.produce_zeros_next = True
                #self.zeros_to_produce = 4096
                #    self.no_input_counter = 0
                time.sleep(1.0 / self.samp_rate * 4096)
                self.consume(0, 0)
                #return -1
                # TODO: check for got_sob or got_eob -> don't add zeros if
                # so!!!
                #print "DEBUG: sim_source - waiting for items"
                output_items[0] = n_requested_samples * [0]
                self.zeros_to_produce -= 4096
                break
       #     else:
                # Wait for input with sob tag
                # ---> Problem: Status kann nicht auftreten, dann
                # zeros_to_produce erst nach dem auftreten des sob tags
                # bekannt!
       #         dbg = "else"
                #print "Case not handled"
       #         output_items[0] = []
       #         break
        n_processed = len(output_items[0])
        self.virtual_counter += n_processed
        #print "DEBUG: req samp before:", self.n_requested_samples
        before = "before"
        if self.n_requested_samples >= 0:
            before_gt = True
            before = self.n_requested_samples
        else:
            before_gt = False
        self.n_requested_samples -= n_processed
        if dbg_late:
            print "DEBUG: Underrun of req_samples:"
            print "-------- before: %s --- after: %s" % (before, self.n_requested_samples)
            print "-------- DBG: %s" % dbg
            print "produce_z_next:", self.produce_zeros_next
            print "n_req_samp", n_requested_samples
            print "len in", len(input_items[0])
            print "produce zeros", self.produce_zeros
            print "got_sob_eob", self.got_sob_eob
            print "samples_to_tx:", self.samples_to_tx
            print "zeros to produce", self.zeros_to_produce
            print "len output_items:", len(output_items[0])
        #print "DEBUG: req samp after:", self.n_requested_samples
        self.twisted_conn.condition.release()
        #print "DEBUG: Sim_sink produced:", n_processed
        return n_processed

    def set_n_requested_samples(self, number_of_samples):
        if number_of_samples < 0:
            print "DEBUG: Number of requested samples is smaller than 0!"
        self.n_requested_samples += number_of_samples

    def set_connection(self, twisted_conn):
        self.twisted_conn = twisted_conn

    def set_dataport(self, port):
        self.dataport = port
        print '[INFO] WiNeLo - Port %s will be used for data transmission' % self.dataport

    def get_dataport(self):
        while self.dataport is None:
            #print "DEBUG: Waiting for dataport"
            #reactor.callFromThread(time.sleep, 0.5)
            reactor.wakeUp()
            time.sleep(0.5)
        return self.dataport

    def refresh_virtual_counter(self, processed_items):
        self.virtual_counter += processed_items

    def evaluate_timestamps(self, nread, ninput_items):
        tags = self.get_tags_in_range(0, nread, nread + ninput_items, pmt.pmt_string_to_symbol("tx_time"))
        if tags:
            #for i in range(0, len(tags)):
                #full_secs = pmt.pmt_to_uint64(pmt.pmt_tuple_ref(tags[i].value, 0))
                #frac_secs = pmt.pmt_to_double(pmt.pmt_tuple_ref(tags[i].value, 1))
                #tx_item = full_secs * self.samp_rate + int(frac_secs / (1.0 / self.samp_rate))
                #if tx_item > self.last_tx_item:
                #    if (len(self.tx_items) is 0) or (tx_item > self.tx_items[len(self.tx_items) - 1]):
                #self.tags['tx_time'].append(tx_item)
            full_secs = pmt.pmt_to_uint64(pmt.pmt_tuple_ref(tags[0].value, 0))
            frac_secs = pmt.pmt_to_double(pmt.pmt_tuple_ref(tags[0].value, 1))
            tx_item = full_secs * self.samp_rate + int(frac_secs / (1.0 / self.samp_rate))
            #if tx_item > self.last_tx_item:
            #    if (len(self.tx_items) is 0) or (tx_item > self.tx_items[len(self.tx_items) - 1]):
            self.tags['tx_time'].append(tx_item)

        sob_tags = self.get_tags_in_range(0, nread, nread + ninput_items, pmt.pmt_string_to_symbol("tx_sob"))
        if sob_tags:
            #for sob_tag in sob_tags:
                #if (sob_tag.offset) > self.last_sob_item:
                #    if (len(self.sob_items) is 0) or ((sob_tag.offset) > self.sob_items[len(self.sob_items) - 1]):
                #self.tags['tx_sob'].append(sob_tag.offset)
            self.tags['tx_sob'].append(sob_tags[0].offset)

        eob_tags = self.get_tags_in_range(0, nread, nread + ninput_items, pmt.pmt_string_to_symbol("tx_eob"))
        if eob_tags:
            #for i in range(0, len(eob_tags)):
                #if (eob_tags[i].offset) > self.last_eob_item:
                #    if (len(self.eob_items) is 0) or ((eob_tags[i].offset) > self.eob_items[len(self.eob_items) - 1]):
                #self.tags['tx_eob'].append(eob_tags[i].offset)
            self.tags['tx_eob'].append(eob_tags[0].offset)

    def get_time_now(self):
        # Calculate time according tot the sample rate & the number of processed items
        time = 1.0 / self.samp_rate * self.virtual_counter
        full_secs = int(time)
        frac_secs = time - int(time)
        # Return full & fractional seconds (like UHD)
        return full_secs, frac_secs


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
            #self.tcp_sink = grc_blks2.tcp_sink(itemsize=gr.sizeof_gr_complex,
            #                                   addr=serverip,
            #                                   port=simsnk.get_dataport(),
            #                                   server=False)
            self.tcp_sink = gr.udp_sink(itemsize=gr.sizeof_gr_complex,
                                        host=serverip,
                                        port=simsnk.get_dataport())
            self.gain_blk = blocks.multiply_const_vcc((1, ))
            self.heartbeat = heart_beat(0.1, "", "")
            self.connect(self.heartbeat, (simsnk, 1))
            self.connect(self, self.gain_blk, (simsnk, 0), self.tcp_sink)
