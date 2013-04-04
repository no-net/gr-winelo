#!/usr/bin/python
"""
Connects to a server and sends data upon request. Additionaly data can be
received. The client differentiates between request and received data using a
very simple header
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor

import struct
import threading

# disable Warnings for invalid classnames used by twisted
#pylint: disable=C0103

# disable warning for missing __init__method, since we inherit from twisted all
# our classes should be fine
#pylint: disable=W0232

# pylint can't find some of the twisted stuff
#pylint: disable=E1101


class SendStuff(Protocol):
    """
    Basic twisted-protocol-implementation. E.g. what to do when data is received
    on a network socket.
    """
    def __init__(self, factory, flowgraph, info):
        self.info = info
        self.flowgraph = flowgraph
        self.flowgraph.set_connection(self)
        self.data = ''
        self.factory = factory
        self.packet_size = self.info['packet_size']
        self.packet_element_size = 8
        self.condition = threading.Condition()

    def connectionMade(self):
        """
        Called as soon as the client connected to the server. The client will
        then start transmitting information about itself to the server.
        """
        print 'Connection to the server established'
        self.transport.write('nameEOH' + self.info['name'] + 'EOP')
        self.transport.write('typeEOH' + self.info['type'] + 'EOP')
        self.transport.write('packet_sizeEOH' + str(self.info['packet_size']) + 'EOP')

    def connectionLost(self, reason):
        """
        Called when the client loses the connection to the server.
        """
        # FIXME maybe this method should also kill the gnuradio flowchart
        print 'Connection lost'

    def dataReceived(self, recvdata):
        """
        Called automatically when the client receives some data. The data's
        header is then checked.
        """
        # join the new received data with the old unprocessed data
        self.data = self.data + recvdata
        # get the first header of the data stream
        header, rest = self.data.split('EOH', 1)
        if header == 'request':
            # the payload is written up to End of Packet
            payload, self.data = rest.split('EOP', 1)
            self.dataRequest(int(payload))
        elif header == 'packetsize':
            payload, self.data = rest.split('EOP', 1)
            self.packet_size = int(payload)
        elif header == 'data':
            # have we received a complete packet?
            if len(rest) >= (self.packet_size * 8 + 3):
                # if samples were transmitted we can't use EOP since the data
                # stream might contain the same sequence. Therefore we have to
                # resort to the lenght of a packet to find its end
                payload = rest[:self.packet_size * 8]
                # the +3 removes the EOP flag from the data
                self.data = rest[(self.packet_size * 8 + 3):]
                self.samplesReceived(payload)
            else:
                # do nothing and wait for the rest to arrive
                return None
        else:
            print 'Error: a header was not decoded correctly'

        if len(self.data) > 0:
            reactor.callWhenRunning(self.dataReceived, '')

    def dataRequest(self, number_of_samples):
        """
        If samples were requested increase the number of requested samples in
        the gnuradio flowgraph
        """
        self.condition.acquire()
        self.flowgraph.set_n_requested_samples(number_of_samples)
        self.condition.notify()
        self.condition.release()

    def samplesReceived(self):
        """
        Called when the header checked out to be data
        """
        #self.condition.acquire()
        #self.flowgraph.new_samples_received(samples)
        reactor.callFromThread(self.transport.write, 'ackEOHdummyEOP')
        #self.condition.notify()
        #self.condition.release()

    def sendSamples(self, samples):
        msg = ''
        for sample in samples:
            msg += struct.pack('f', sample.real) + struct.pack('f', sample.imag)
        reactor.callFromThread(self.transport.write, 'dataEOH' + msg + 'EOP')


class SendFactory(ClientFactory):
    """
    Our factory builds a protocol for an established connection.
    """
    def __init__(self, connection, info):
        self.info = info
        self.connection = connection

    def buildProtocol(self, addr):
        """
        Return our custom protocol.
        """
        return SendStuff(self, self.connection, self.info)


class uhd_gate(object):
    """
    WiNeLo UHD wrapper.
    """
    def __init__(self, gain_range=(0, 45, 0.05), center_freq=100000000):
        self.gain_range = gain_range
        self.center_freq = center_freq

    def set_start_time(self, uhd_time):
        if self.simulation:
            print "Not supported by WiNeLo: set_start_time"
            #print "Send start time to server"  # DO
        else:
            self.usrp.set_start_time(uhd_time)

    def issue_stream_command(self, cmd):
        if self.simulation:
            print "Not supported by WiNeLo: issue_stream_command"
        else:
            self.usrp.issue_stream_command(cmd)

    def get_usrp_info(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_usrp_info"
            #return {"WiNeLo block type": "source"}  # DO: output packet_size etc.
        else:
            self.usrp.get_usrp_info(chan)

    def set_subdev_spec(self, spec, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_subdev_spec"
        else:
            self.usrp.set_subdev_spec(spec, mboard)

    def get_subdev_spec(self, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_subdev_spec"
        else:
            self.usrp.get_subdev_spec(mboard)

    def set_samp_rate(self, rate):
        if self.simulation:
            print "Not supported by WiNeLo: set_samp_rate"
            #print "Set samp_rate on server"  # DO: Set samp_rate on server
        else:
            self.usrp.set_samp_rate(rate)

    def get_samp_rate(self):
        if self.simulation:
            print "Not supported by WiNeLo: get_samp_rate"
            #samprate_server = "rate from server"  # DO: Get samp_rate from server
            #return samprate_server
        else:
            return self.usrp.get_samp_rate()

    def set_center_freq(self, freq, chan=0):
        if self.simulation:
            print "Set freq on server"  # TODO: Set freq on server -> multiple channels!
        else:
            self.usrp.set_center_freq(freq, chan)

    def get_center_freq(self, chan=0):
        if self.simulation:
            print "Get freq from server"  # TODO: Get freq from server
        else:
            return self.usrp.get_center_freq(chan)

    def get_freq_range(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_freq_range"
            #return "freq_range"  # DO: uhd.freq_range 0 - 1000000000
        else:
            return self.usrp.get_center_freq(chan)

    def set_gain(self, gain, chan=0):
        if self.simulation:
            if gain in self.gain_range:
                self.gain_blk.set_k((gain, ))
        else:
            self.usrp.set_gain(gain, chan)

    def get_gain(self, chan=0):
        if self.simulation:
            return self.gain_blk.k()
        else:
            return self.usrp.get_gain(chan)

    def get_gain_names(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_gain_names"
            #return ("WiNeLo-gain")
        else:
            return self.usrp.get_gain_names(chan)

    def get_gain_range(self, chan=0):
        if self.simulation:
            return self.gain_range
        else:
            return self.usrp.get_gain_range(chan)

    def set_antenna(self, ant, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_antenna"
        else:
            self.usrp.set_antenna(ant, chan)

    def get_antenna(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_antenna"
            #return 'TX/RX'
        else:
            return self.usrp.get_antenna(chan)

    def get_antennas(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_antennas"
            #return ('TX/RX')
        else:
            return self.usrp.get_antennas(chan)

    def set_bandwidth(self, bw, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_bandwidth"
        else:
            self.usrp.set_bandwidth(bw, chan)

    def set_auto_dc_offset(self, enb, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_auto_dc_offset"
        else:
            self.usrp.set_auto_dc_offset(enb, chan)

    def set_dc_offset(self, offset, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_dc_offset"
        else:
            self.usrp.set_dc_offset(offset, chan)

    def set_iq_balance(self, correction, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_iq_balance"
        else:
            self.usrp.set_iq_balance(correction, chan)

    def get_sensor(self, name, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_sensor"
        else:
            return self.usrp.get_sensor(name, chan)

    def get_sensor_names(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_sensor_names"
            return ()
        else:
            return self.usrp.get_sensor_names(chan)

    def get_mboard_sensor(self, name, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_mboard_sensor"
        else:
            return self.usrp.get_mboard_sensor(name, chan)

    def get_mboard_sensor_names(self, chan=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_sensor_names"
            return ()
        else:
            return self.usrp.get_mboard_sensor_names(chan)

    def set_time_source(self, source, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_time_source"
        else:
            self.usrp.set_time_source(source, mboard)

    def get_time_source(self, mboard):
        if self.simulation:
            print "Not supported by WiNeLo: get_time_source"
            #return 'WiNeLo'
        else:
            return self.usrp.get_time_source(mboard)

    def get_time_sources(self, mboard):
        if self.simulation:
            print "Not supported by WiNeLo: get_time_sources"
            #return ('WiNeLo')
        else:
            return self.usrp.get_time_sources(mboard)

    def set_clock_source(self, source, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_clock_source"
        else:
            self.usrp.set_clock_source(source, mboard)

    def get_clock_source(self, mboard):
        if self.simulation:
            print "Not supported by WiNeLo: get_clock_source"
            #return 'WiNeLo'
        else:
            return self.usrp.get_clock_source(mboard)

    def get_clock_sources(self, mboard):
        if self.simulation:
            print "Not supported by WiNeLo: get_clock_sources"
            #return ('WiNeLo')
        else:
            return self.usrp.get_clock_sources(mboard)

    def set_clock_rate(self, rate, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_clock_rate"
        else:
            self.usrp.set_clock_rate(rate, mboard)

    def get_clock_rate(self, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: get_clock_rate"
            #return 'WiNeLo'
        else:
            return self.usrp.get_clock_rate(mboard)

    def get_time_now(self, mboard=0):
        if self.simulation:
            return 'WiNeLo-time'  # TODO: Return time from server!
        else:
            return self.usrp.get_time_now(mboard)

    def get_time_last_pps(self, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_time_last_pps"
            #return 'WiNeLo-PPS'  #  DO: Return last full sec  from server!
        else:
            return self.usrp.get_time_last_pps(mboard)

    def set_time_now(self, time_spec, mboard=0):
        if self.simulation:
            print "Not supported by WiNeLo: set_time_now"
            #return 'WiNeLo-time'  # DO: Set time in server now!
        else:
            self.usrp.set_time_now(time_spec, mboard)

    def set_time_next_pps(self, time_spec):
        if self.simulation:
            print "Not supported by WiNeLo: set_time_next_pps"
            #return 'WiNeLo-PPS'  # DO: Set time req next full sec in server!
        else:
            self.usrp.set_time_next_pps(time_spec)

    def set_time_unknown_pps(self, time_spec):
        if self.simulation:
            print "Not supported by WiNeLo: set_time_unknown_pps"
        else:
            self.usrp.set_time_unknown_pps(time_spec)

    def set_command_time(self, time_spec, mboard=0):
        if self.simulation:
            print 'Set WiNeLo-commandtime'  # TODO: Send command-time to server!
        else:
            self.usrp.set_command_time(time_spec, mboard)

    def clear_command_time(self, mboard=0):
        if self.simulation:
            print 'clear WiNeLo-commandtime'  # TODO: Clear command-time on server!
        else:
            self.usrp.clear_command_time(mboard)
