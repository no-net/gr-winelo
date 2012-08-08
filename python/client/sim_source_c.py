import numpy
from gnuradio import gr

from twisted.internet import reactor
import thread
from winelo.client import SendFactory
import winelo.common.hwprofile

import time

class sim_source_c(gr.sync_block):
    def __init__(self, serverip, serverport, clientname,
                clientindex, packetsize, startreactor,
                noise_ampl, inphase_ampl, quadrature_ampl,
                phase_noise_ampl, freq_offset, hwemu_on_client):
        gr.sync_block.__init__(
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
        # hardware profile that can be transmitted to the server if the server
        # is responsible for emulation the hardware. Otherwise the client does
        # this. Copy is needed since otherwise we would only have a reference
        # to the profile
        self.hwemu_on_client = hwemu_on_client
        self.hwprofile = winelo.common.hwprofile.hwprofile.copy()
        self.hwprofile.update({  'noise_ampl':noise_ampl,
                            'inphase_ampl':inphase_ampl,
                            'quadrature_ampl':quadrature_ampl,
                            'phase_noise_ampl':phase_noise_ampl,
                            'freq_offset':freq_offset,
                        })
        # connect to the server
        reactor.connectTCP(serverip, serverport, SendFactory(self,
            {'type':'rx','name':clientname, 'index':clientindex,
            'packet_size':packetsize, 'hwprofile':self.hwprofile,
            'hwemu_on_client':self.hwemu_on_client}))
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

    def set_noise_ampl(self, ampl):
        # if we do the emulation on the client we can directly change our
        # hwprofile, since the twisted client uses the same profile because
        # dictionaries are passed as references.
        if self.hwemu_on_client:
            self.hwprofile['noise_ampl'] = ampl
        # otherwise we have to send the new value to the server
        else:
            self.connection.transport.write('profileEOH' + 'noise_ampl:' + str(ampl) + 'EOP')

    def set_inphase_ampl(self, ampl):
        if self.hwemu_on_client:
            self.hwprofile['inphase_ampl'] = ampl
        else:
            self.connection.transport.write('profileEOH' + 'inphase_ampl:' + str(ampl) + 'EOP')

    def set_quadrature_ampl(self, ampl):
        if self.hwemu_on_client:
            self.hwprofile['quadrature_ampl'] = ampl
        else:
            self.connection.transport.write('profileEOH' + 'quadrature_ampl:' + str(ampl) + 'EOP')

    def set_phase_noise_ampl(self, ampl):
        if self.hwemu_on_client:
            self.hwprofile['phase_noise_ampl'] = ampl
        else:
            self.connection.transport.write('profileEOH' + 'phase_noise_ampl:' + str(ampl) + 'EOP')

    def set_freq_offset(self, freq):
        if self.hwemu_on_client:
            self.hwprofile['freq_offset'] = freq
        else:
            self.connection.transport.write('profileEOH' + 'freq_offset:' + str(freq) + 'EOP')
