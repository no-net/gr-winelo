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
import numpy

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
        self.dbg_counter = 0

    def connectionMade(self):
        """
        Called as soon as the client connected to the server. The client will
        then start transmitting information about itself to the server.
        """
        print '[INFO] WiNeLo - Connection to the server established'
        #self.transport.write('nameEOH' + self.info['name'] + 'EOP')
        #self.transport.write('typeEOH' + self.info['type'] + 'EOP')
        #self.transport.write('packet_sizeEOH' + str(self.info['packet_size']) + 'EOP')
        reactor.callFromThread(self.transport.write, ('nameEOH' + self.info['name'] + 'EOP'))
        reactor.callFromThread(self.transport.write, ('centerfreqEOH' + str(self.info['centerfreq']) + 'EOP'))
        reactor.callFromThread(self.transport.write, ('samprateEOH' + str(self.info['samprate']) + 'EOP'))
        reactor.callFromThread(self.transport.write, ('typeEOH' + self.info['type'] + 'EOP'))
        reactor.callFromThread(self.transport.write, ('packet_sizeEOH' + str(self.info['packet_size']) + 'EOP'))

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
        #print "DEBUG: client received:", recvdata
        self.data = self.data + recvdata

        if len(self.data) > 0:
            #print "DEBUG: Client - Werte data aus:", self.data
            # get the first header of the data stream
            header, rest = self.data.split('EOH', 1)
            if header == 'request':
                # the payload is written up to End of Packet
                payload, self.data = rest.split('EOP', 1)
                self.dataRequest(int(payload))
            elif header == 'packetsize':
                payload, self.data = rest.split('EOP', 1)
                self.packetsizeReceived(int(payload))
                self.packet_size = int(payload)
            elif header == 'dataport':
                payload, self.data = rest.split('EOP', 1)
                self.dataportReceived(int(payload))
            elif header == 'virttimeoffset':
                payload, self.data = rest.split('EOP', 1)
                self.virttimeReceived(float(payload))
            else:
                print '[ERROR] WiNeLo - a header was not decoded correctly'

        if len(self.data) > 0:
            reactor.callFromThread(self.dataReceived, '')

    def dataRequest(self, number_of_samples):
        """
        If samples were requested increase the number of requested samples in
        the gnuradio flowgraph
        """
        self.condition.acquire()
        self.dbg_counter += 1
        #print "DEBUG: Client %s - Request received: %s - This is Req. no. %s" % (self.info['name'], number_of_samples, self.dbg_counter)
        self.flowgraph.set_n_requested_samples(number_of_samples)
        #print "DEBUG: Set request!"
        self.condition.notify()
        self.condition.release()

    def dataportReceived(self, dataport):
        """
        Set port used for tcp source/sink.
        """
        self.condition.acquire()
        self.flowgraph.set_dataport(dataport)
        self.condition.notify()
        self.condition.release()

    def packetsizeReceived(self, packet_size):
        """
        Set port used for tcp source/sink.
        """
        self.condition.acquire()
        self.flowgraph.set_packetsize(packet_size)
        self.condition.notify()
        self.condition.release()

    def virttimeReceived(self, virttime_offset):
        """
        Set port used for tcp source/sink.
        """
        self.condition.acquire()
        self.flowgraph.update_virttime(virttime_offset)
        self.condition.notify()
        self.condition.release()

    def samplesReceived(self):
        """
        Called when the header checked out to be data
        """
        #print "DEBUG: client called samples received"
        reactor.callFromThread(self.transport.write, 'ackEOHdummyEOP')


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

    def clientConnectionFailed(self, connection, reason):
        print '[ERROR] WiNeLo - Connection failed:', reason

    def clientConnectionLost(self, connection, reason):
        print '[ERROR] WiNeLo - Connection lost:', reason


class uhd_gate(object):
    """
    WiNeLo UHD wrapper.
    """
    def __init__(self, gain_range=(0, 45, 0.05), center_freq=100000000):
        self.gain_range = gain_range
        self.center_freq = center_freq
        self.collecting_timed_commands = False
        self.commands = []
        self.command_times = []
        self.samp_rate = 0

    def set_start_time(self, uhd_time):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_start_time"
            #print "Send start time to server"  # DO
        else:
            self.usrp.set_start_time(uhd_time)

    def issue_stream_command(self, cmd):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: issue_stream_command"
        else:
            self.usrp.issue_stream_command(cmd)

    def get_usrp_info(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_usrp_info"
            #return {"WiNeLo block type": "source"}  # DO: output packet_size etc.
        else:
            self.usrp.get_usrp_info(chan)

    def set_subdev_spec(self, spec, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_subdev_spec"
        else:
            self.usrp.set_subdev_spec(spec, mboard)

    def get_subdev_spec(self, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_subdev_spec"
        else:
            self.usrp.get_subdev_spec(mboard)

    def set_samp_rate(self, rate):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_samp_rate"
            #print "Set samp_rate on server"  # DO: Set samp_rate on server
            self.samp_rate = rate  # TODO: Really change rate of fg!
        else:
            self.usrp.set_samp_rate(rate)

    def get_samp_rate(self):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_samp_rate"
            #samprate_server = "rate from server"  # DO: Get samp_rate from server
            return self.samp_rate  # TODO: Return real fg samp_rate!
        else:
            return self.usrp.get_samp_rate()

    def set_center_freq(self, freq, chan=0, collected_cmd=False):
        if self.simulation:
            #print "Set freq on server: ", freq  # TODO: Set freq on server -> multiple channels!
            if not self.collecting_timed_commands or collected_cmd:
                if self.typ == 'rx':
                    reactor.callFromThread(self.simsrc.twisted_conn.transport.write, ('centerfreqEOH' + str(freq) + 'EOP'))
                else:
                    reactor.callFromThread(self.simsnk.twisted_conn.transport.write, ('centerfreqEOH' + str(freq) + 'EOP'))
            else:
                #print "DEBUG: appending command - cmd-times %s - cmds %s!" % (self.command_times, self.commands)
                self.commands.append([self.set_center_freq, [freq, chan, True]])
                #print "DEBUG"
                self.command_times[-1][1] += 1
                #print "DEBUG: cmd times:", self.command_times
            return True
        else:
            self.usrp.set_center_freq(freq, chan)

    def get_center_freq(self, chan=0):
        if self.simulation:
            print "Get freq from server"  # TODO: Get freq from server
        else:
            return self.usrp.get_center_freq(chan)

    def get_freq_range(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_freq_range"
            #return "freq_range"  # DO: uhd.freq_range 0 - 1000000000
        else:
            return self.usrp.get_center_freq(chan)

    def set_gain(self, gain_db, chan=0):
        if self.simulation:
            gain = numpy.power(10, gain_db)
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
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_gain_names"
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
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_antenna"
        else:
            self.usrp.set_antenna(ant, chan)

    def get_antenna(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_antenna"
            #return 'TX/RX'
        else:
            return self.usrp.get_antenna(chan)

    def get_antennas(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_antennas"
            #return ('TX/RX')
        else:
            return self.usrp.get_antennas(chan)

    def set_bandwidth(self, bw, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_bandwidth"
        else:
            self.usrp.set_bandwidth(bw, chan)

    def set_auto_dc_offset(self, enb, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_auto_dc_offset"
        else:
            self.usrp.set_auto_dc_offset(enb, chan)

    def set_dc_offset(self, offset, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_dc_offset"
        else:
            self.usrp.set_dc_offset(offset, chan)

    def set_iq_balance(self, correction, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_iq_balance"
        else:
            self.usrp.set_iq_balance(correction, chan)

    def get_sensor(self, name, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_sensor"
        else:
            return self.usrp.get_sensor(name, chan)

    def get_sensor_names(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_sensor_names"
            return ()
        else:
            return self.usrp.get_sensor_names(chan)

    def get_mboard_sensor(self, name, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_mboard_sensor"
        else:
            return self.usrp.get_mboard_sensor(name, chan)

    def get_mboard_sensor_names(self, chan=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_sensor_names"
            return ()
        else:
            return self.usrp.get_mboard_sensor_names(chan)

    def set_time_source(self, source, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_time_source"
        else:
            self.usrp.set_time_source(source, mboard)

    def get_time_source(self, mboard):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_time_source"
            #return 'WiNeLo'
        else:
            return self.usrp.get_time_source(mboard)

    def get_time_sources(self, mboard):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_time_sources"
            #return ('WiNeLo')
        else:
            return self.usrp.get_time_sources(mboard)

    def set_clock_source(self, source, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_clock_source"
        else:
            self.usrp.set_clock_source(source, mboard)

    def get_clock_source(self, mboard):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_clock_source"
            #return 'WiNeLo'
        else:
            return self.usrp.get_clock_source(mboard)

    def get_clock_sources(self, mboard):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_clock_sources"
            #return ('WiNeLo')
        else:
            return self.usrp.get_clock_sources(mboard)

    def set_clock_rate(self, rate, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_clock_rate"
        else:
            self.usrp.set_clock_rate(rate, mboard)

    def get_clock_rate(self, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: get_clock_rate"
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
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_time_last_pps"
            #return 'WiNeLo-PPS'  #  DO: Return last full sec  from server!
        else:
            return self.usrp.get_time_last_pps(mboard)

    def set_time_now(self, time_spec, mboard=0):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_time_now"
            #return 'WiNeLo-time'  # DO: Set time in server now!
        else:
            self.usrp.set_time_now(time_spec, mboard)

    def set_time_next_pps(self, time_spec):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_time_next_pps"
            #return 'WiNeLo-PPS'  # DO: Set time req next full sec in server!
        else:
            self.usrp.set_time_next_pps(time_spec)

    def set_time_unknown_pps(self, time_spec):
        if self.simulation:
            print "[WARNING] WiNeLo - Not supported by WiNeLo: set_time_unknown_pps"
        else:
            self.usrp.set_time_unknown_pps(time_spec)

    def set_command_time(self, time_spec, mboard=0):
        if self.simulation:
            #print 'Set WiNeLo-commandtime: %s' % time_spec.get_real_secs()  # TODO: Send command-time to server!
            self.command_times.append([time_spec.get_real_secs(), 0])
            self.collecting_timed_commands = True
        else:
            self.usrp.set_command_time(time_spec, mboard)

    def clear_command_time(self, mboard=0):
        if self.simulation:
            #print 'clear WiNeLo-commandtime'  # TODO: Clear command-time on server!
            self.collecting_timed_commands = False
        else:
            self.usrp.clear_command_time(mboard)
