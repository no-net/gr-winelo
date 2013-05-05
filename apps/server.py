#!/usr/bin/python
"""
Sets up a server listening on a speciefied port. As soon as a client connects,
the server starts to request data. The interval can be configured
in the class SyncFactory. At fixed intervals the server also synchronizes the
streams of the client and transmit data to them. This interval can also be set
in the same class SyncFactory.
"""

from twisted.internet.protocol import Protocol, ServerFactory
from twisted.internet import reactor

from gnuradio import gr

import argparse
import numpy

# importing stuff that is responsible for simulating the channel in gnuradio
import winelo
import time

import threading

# disable Warnings for invalid classnames used by twisted
#pylint: disable=C0103

# disable warning for missing __init__method, since we inherit from twisted all
# our classes should be fine
#pylint: disable=W0232

# pylint can't find some of the twisted stuff
#pylint: disable=E1101

import struct


class Sync(Protocol):
    """
    Custom protocol that handles the communication with a connected client.
    """
    def __init__(self, factory):
        """
        Sets some initial information and provides the information of all
        connections to the client.
        """
        # self.data contains the received data, which will later on be converted
        # into samples
        self.data = ''
        # self.samples contains the received samples
        self.samples = numpy.zeros(factory.packet_size, dtype=complex)
        # self.info contains information about the connected client
        self.info = {}
        # name of the connected client, must be unique
        self.info['name'] = None
        # type of the client
        # tx: produces samples
        # rx: consumes samples
        self.info['type'] = None
        # depending on the type, different GNU Radio blocks are used to connect
        # the client to the channel flowgraph.
        self.info['block'] = None
        # Dictionary that will contain all the channels from a
        # transmitter to all receivers. The channels are accessed via the name
        # of the receiver
        self.info['channels'] = {}
        # maximum packet size supported by this client
        self.info['packet_size'] = None
        # The port is simply calculated by the number of known clients + server
        # port
        client_no = len(factory.clients['rx'] + factory.clients['tx'])
        self.info['dataport'] = factory.serverport + client_no + 1
        # self.factory provides the information of all connections
        # to this client
        self.factory = factory
        # flag that is relevant for txs. The flag is set when all requested
        # samples have arrived and were passed to the channel flowgraph
        self.samples_passed_2_gr = False
        # flag used by rx if they have received their stuff
        self.ack_received = False
        # Threading condition that manages the data exchange between GNU Radio
        # and Twisted.
        self.condition = threading.Condition()
        self.kill = False

    def connectionMade(self):
        """Called automatically when a new client connects.

        When a new client connects it will immediately start sending some
        initial information about itself, like its name, type, etc.
        """
        print 'A client just connected'
        # send the currently used packet size to the client
        #self.transport.write('packetsizeEOH%iEOP' % self.factory.packet_size)
        self.transport.write('packetsizeEOH%iEOPdataportEOH%iEOP' % (self.factory.packet_size, self.info['dataport']))
        #self.transport.write('dataportEOH%iEOP' % self.info['dataport'])
        # set the connect in process flag
        # No new packets of samples due to received acks from the receivers will
        # be requested from the transmitters will a connect is in process.
        self.factory.connect_in_process = True

    def connectionLost(self, reason):
        """ Called automatically when the connection to a client is lost.

        This method basicially does some clean-up.
        """
        # set the disconnect in process flag
        # No new packets of samples due to received acks from the receivers will
        # be requested from the transmitters will a disconnect is in process.
        self.factory.disconnect_in_process = True
        print 'Connection lost to client %s' % self.info['name']
        # if the disconnecting client is a transmitter and has not yet passed
        # its samples to the channel flowgraph a packet of dummy samples is used
        # instead, so that the flowgraph has a complete set of packets available
        # from every client and can finish processing
        if self.info['type'] is 'tx' and not self.samples_passed_2_gr:
            self.info['block'].samples_received(numpy.zeros(self.factory.packet_size))
            self.data = ''

        # The GNU Radio channel flowgraph runs in a separate thread.
        # reactor.callLater will give this thread time to finish before
        # adjusting the flowgraph.
        # FIXME variable delay
        reactor.callLater(1, self.unregisterClient)

    def unregisterClient(self):
        """ Called when a client disconnected """
        # teardown the channel
        self.factory.channel.teardown_channel()

        # delete this client from the list of all connected clients
        self.factory.clients[self.info['type']].remove(self)

        # rebuild the channel
        self.factory.channel.rebuild_channel()
        self.factory.disconnect_in_process = False

        self.factory.updatePacketSize()

        # Request new samples from all connected transmitters, since no new
        # samples were requested while the channel flowgraph was shutting down.
        for tx in self.factory.clients['tx']:
            reactor.callFromThread(tx.reqData, tx.factory.packet_size)

    def dataReceived(self, recvdata):
        """
        This method is automatically called as soon the the server receives data
        from this client. Depending on the header different methods are called
        to work on the load of this packet.

        A complete package looks like this:
        headerEOHpayloadEOP
        EOH: End Of Header
        EOP: End Of Packet
        """
        handleheaders = {'name': self.setName,
                         'type': self.setType,
                         'packet_size': self.setPacketSize,
                         'ack': self.handleAck,
                         }

        # join the new received data with the old unprocessed data
        self.data = self.data + recvdata

        if len(self.data) > 0:
            # get the first header of the data stream
            try:
                header, rest = self.data.split('EOH', 1)
            except ValueError:
                print 'Could not extract a complete header'
                print 'waiting for further data'
                print self.info
                return None
            try:
                payload, self.data = rest.split('EOP', 1)
            except ValueError:
                return None

            # Call different methods, depending of the header.
            try:
                handleheaders[header](payload)
            except KeyError:
                # This should never happen. Just some debug output.
                print self.info['name'], ' header: ', header
                print self.info['name'], ' payload: ', payload

        # This if statement ensures, that if multiple packages are stored in
        # self.data all of them are processed
        if len(self.data) > 0:
            reactor.callFromThread(self.dataReceived, '')

    def setType(self, clienttype):
        """
        Sets the type of the client:
        tx: client produces samples
        rx: client consumes samples
        Depending of the type of the client it is assigned a different
        connection-block for the GNU Radio flowgraph
        """
        self.info['type'] = clienttype
        if clienttype == 'tx':
            self.info['block'] = winelo.server.tw2gr_c(self, "127.0.0.1", self.info['dataport'])
        else:
            self.info['block'] = winelo.server.gr2tw_c(self, "127.0.0.1", self.info['dataport'])

    def setName(self, name):
        """
        Sets the name of this client
        """
        self.info['name'] = name

    def setPacketSize(self, packet_size):
        """
        Sets the packet size of this client and registers the client
        """
        self.info['packet_size'] = int(packet_size)
        # All relevant information about this clien was received. Teardown the
        # current GNU Radio channel flowgraph and connect this client to the new channel
        # flowgraph.
        # The GNU Radio channel flowgraph runs in a separate thread.
        # reactor.callLater will give this thread time to finish before
        # connecting the new client to a new channel flowgraph.
        # FIXME variable delay
        reactor.callLater(1, self.registerClient)

    def registerClient(self):
        """
        Adds the client to the list of connected clients and update the GNU
        Radio flowgraph
        """
        # Bringing down the channel due to a newly connected client
        self.factory.channel.teardown_channel()

        # Append this client to the list of all clients of the same type
        self.factory.clients[self.info['type']].append(self)
        print self
        print "Port %s will be used for data transmission to/from thislient" % self.info['dataport']

        for tx in self.factory.clients['tx']:
            # new tx blocks are needed, otherwise I always received too many
            # acks. Maybe some samples were still in the flowgraph
            #tx.info['block'] = None
            #tx.info['block'] = winelo.server.tw2gr_c(tx, "127.0.0.1", 8888)
            # Create a channel for each receiver, pass if a channel already
            # exists.
            for rx in self.factory.clients['rx']:
                if rx.info['name'] in tx.info['channels']:
                    pass
                else:
                    tx.info['channels'][rx.info['name']] = self.factory.channel_model(**self.factory.args.opts)

        # After a new client connected sucessfully, update the packet size which
        # will be used from now on.
        self.factory.updatePacketSize()
        self.factory.channel.rebuild_channel()

        self.factory.connect_in_process = False

        # Request new samples from all connected transmitters, since no new
        # samples were requested while the channel flowgraph was shutting down.
        for tx in self.factory.clients['tx']:
            reactor.callFromThread(tx.reqData, self.factory.packet_size)

    def handleAck(self, dummy):
        """
        Request new data from all transmitters, if an ack was received from all
        receivers.
        """
        #print "DEBUG: Server - ACK received from %s" % self.info['name']
        self.ack_received = True
        # has the ack been received from all receivers
        all_acks_received = False not in [rx.ack_received for rx in self.factory.clients['rx']]
        #print "DEBUG: Server - all_acks_received: %s" % all_acks_received
        # if all acks have been received and no client is currently connecting
        # or disconnecting request new data from all transmitters
        if all_acks_received and not (self.factory.connect_in_process or self.factory.disconnect_in_process):
            for tx in self.factory.clients['tx']:
                reactor.callFromThread(tx.reqData, tx.factory.packet_size)
            for rx in self.factory.clients['rx']:
                rx.ack_received = False

    def __str__(self):
        """
        Overloading the __str__ method, so that "print client" does something
        meaningful
        """
        return 'Client \"%s\" is of type \"%s\" and supports a maximum packet size of \"%i\" ' % (
            self.info['name'], self.info['type'], self.info['packet_size'])

    def reqData(self, number_of_samples):
        """
        Request a packet of size self.factory.packet_size from a client
        """
        #print 'DEBUG: Server - Requested samples from %s' % self.info['name']
        self.transport.write('requestEOH%dEOP' % (number_of_samples))
        self.samples_passed_2_gr = False


class SyncFactory(ServerFactory):
    """
    This class keeps track of connections. Therefore it stores information
    required by all clients and is in charge of synchronizing the
    different data-streams
    """
    def __init__(self, args, channel_model):
        """
        Sets some global parameters for all connected clients.
        """
        self.tic = time.time()
        self.args = args
        self.serverport = args.port
        self.clients = {'tx': [], 'rx': []}
        self.channel = winelo.server.gr_channel(self.clients['tx'],
                                                self.clients['rx']
                                                )
        self.channel_model = channel_model
        self.packet_size = self.args.packetsize
        # Size of one element in packet --> numpy.complex
        self.packet_element_size = 8
        self.package_counter = 0
        self.connect_in_process = False
        self.disconnect_in_process = False

    def buildProtocol(self, addr):
        """
        Returns our custom protocol
        """
        return Sync(self)

    def updatePacketSize(self):
        """
        Sets the packet size used for transmission to the absolute maximum
        supported by all clients.
        """
        # 999999 is added so that min( ... ) always returns a result
        min_tx = min([x.info['packet_size'] for x in self.clients['tx']] + [999999])
        min_rx = min([x.info['packet_size'] for x in self.clients['rx']] + [999999])
        self.packet_size = min(min_tx, min_rx)
        for tx in self.clients['tx']:
            tx.samples = numpy.zeros(self.packet_size, dtype=complex)
            tx.transport.write('packetsizeEOH%iEOP' % self.packet_size)
        for rx in self.clients['rx']:
            rx.transport.write('packetsizeEOH%iEOP' % self.packet_size)
        print 'updated packet_size:', self.packet_size


def main():
    """
    Setup a server, listening on the specified port and waiting for clients to
    connect.
    """

    channel_models = {
        'const': gr.multiply_const_cc,
        'rayleigh': winelo.channel.models.rayleigh_cc,
        'cs_meas': winelo.channel.models.cs_meas_cc,
        'cost207badurban': winelo.channel.models.cost207.bad_urban_cc.paths_6,
        'cost207hillyterrain': winelo.channel.models.cost207.hilly_terrain_cc.paths_6,
        'cost207typicalurban': winelo.channel.models.cost207.typical_urban_cc.paths_6,
        'cost207typicalurban12': winelo.channel.models.cost207.typical_urban_cc.paths_12,
        'cost207ruralarea': winelo.channel.models.cost207.rural_area_cc.paths_4}

    parser = argparse.ArgumentParser(
        description='Starts the gnuradio-channel-simmulation server GRCSS.',
                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--model', '-M', action='store',
                        dest='model', nargs='?',
                        help='name of the channel model to be used. Available models are:\n' + '\n'.join(channel_models.keys()))
    parser.add_argument('--opts', '-O', action='store',
                        dest='opts', nargs='*', help='channel model parameters. Something like:\n[sample_rate 32000 fmax 100] or [k 1]')
    parser.add_argument('--port', '-P', type=int, action='store',
                        dest='port', nargs='?', default=8888,
                        help='the port on which the server is listening')

    parser.add_argument('--packetsize', '-N', type=int, action='store', nargs='?',
                        default=1000, help='How many samples a package will contain')

    args = parser.parse_args()

    # turn the channel model parameters in a dictionary
    args.opts = dict(zip(args.opts[0::2], args.opts[1::2]))
    for key in args.opts.keys():
        # convert the parameters to float, except if the parameter is a string
        # than float() will throw a value error and we don't have to do
        # anything
        try:
            args.opts[key] = float(args.opts[key])
        except ValueError:
            pass
    channel_model = channel_models[args.model]

    reactor.listenTCP(args.port, SyncFactory(args, channel_model))
    print "Server is listening on port %d" % (args.port)
    print "The initial packet size is %i" % (args.packetsize)
    reactor.run()

if __name__ == '__main__':
    main()
