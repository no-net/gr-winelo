#!/usr/bin/python
"""
Connects to a server and sends data upon request. Additionaly data can be
received. The client differentiates between request and received data using a
very simple header
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor

import struct
import numpy
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
        header, rest = self.data.split('EOH',1)
        if header == 'request':
            # the payload is written up to End of Packet
            payload, self.data = rest.split('EOP',1)
            self.dataRequest(int(payload))
        elif header == 'packetsize':
            payload, self.data = rest.split('EOP',1)
            self.packet_size = int(payload)
        elif header == 'data':
            # have we received a complete packet?
            if len(rest)>=(self.packet_size*8+3):
                # if samples were transmitted we can't use EOP since the data
                # stream might contain the same sequence. Therefore we have to
                # resort to the lenght of a packet to find its end
                payload = rest[:self.packet_size*8]
                # the +3 removes the EOP flag from the data
                self.data = rest[self.packet_size*8+3:]
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

    def samplesReceived(self, data):
        """
        Called when the header checked out to be data
        """
        sample_start = 0
        ctr = 0
        samples = numpy.zeros(self.packet_size, dtype = complex)
        while(sample_start < len(data)):
            realpart = struct.unpack('f', data[sample_start:sample_start + 4])[0]
            imagpart = struct.unpack('f', data[sample_start+4:sample_start + 8])[0]
            samples[ctr] = numpy.complex(realpart, imagpart)
            sample_start += 8
            ctr += 1

        self.condition.acquire()
        self.flowgraph.new_samples_received(samples)
        self.transport.write('ackEOHdummyEOP')
        self.condition.notify()
        self.condition.release()

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
