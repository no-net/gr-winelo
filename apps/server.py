#!/usr/bin/python
"""
Sets up a server listening on a speciefied port. As soon as a client connects,
the server starts to request data. The interval can be configured
in the class SyncFactory. At fixed intervals the server also synchronizes the
streams of the client and transmit data to them. This interval can also be set
in the same class SyncFactory.
"""

from twisted.internet import reactor


import argparse

# importing stuff that is responsible for simulating the channel in gnuradio
import winelo


# disable Warnings for invalid classnames used by twisted
#pylint: disable=C0103

# disable warning for missing __init__method, since we inherit from twisted all
# our classes should be fine
#pylint: disable=W0232

# pylint can't find some of the twisted stuff
#pylint: disable=E1101
#
#import struct


def main():
    """
    Setup a server, listening on the specified port and waiting for clients to
    connect.
    """

    channel_models = {
        'const': winelo.channel.models.const_cc,
        'const_multi': winelo.channel.models.const_multi_cc,
        'rayleigh': winelo.channel.models.rayleigh_cc,
        'cs_meas': winelo.channel.models.cs_meas_cc,
        'cost207badurban': winelo.channel.models.cost207.bad_urban_cc.paths_6,
        'cost207hillyterrain':
        winelo.channel.models.cost207.hilly_terrain_cc.paths_6,
        'cost207typicalurban':
        winelo.channel.models.cost207.typical_urban_cc.paths_6,
        'cost207typicalurban12':
        winelo.channel.models.cost207.typical_urban_cc.paths_12,
        'cost207ruralarea': winelo.channel.models.cost207.rural_area_cc.paths_4}
        # TODO: ADD NETWORK CHANNEL MODEL (EXAMPLE WITH 3 NODES)

    hw_models = {
        'none': winelo.hw_models.none_cc,
        'mixing_only': winelo.hw_models.mixing_only_cc,
        'basic': winelo.hw_models.basic_cc}

    parser = argparse.ArgumentParser(
        description='Starts the gnuradio-channel-simmulation server GRCSS.',
                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--model', '-M', action='store',
                        dest='model', nargs='?',
                        help='name of the channel model to be used. Available '
                        'models are:\n' + '\n'.join(channel_models.keys()))
    parser.add_argument('--opts', '-O', action='store',
                        dest='opts', nargs='*', help='channel model parameters.'
                        'Something like:\n[sample_rate 32000 fmax 100] or [k 1]'
                        )
    parser.add_argument('--hw-model', '-H', action='store',
                        dest='hwmodel', nargs='?',
                        help='name of the hw model to be used. Available models'
                        'are:\n' + '\n'.join(hw_models.keys()))
    parser.add_argument('--hw-opts', '-I', action='store',
                        dest='hwopts', nargs='*', help='hw model parameters. '
                        'Something like:\n[noise_ampl 0.0001 f_offset 2000]')
    parser.add_argument('--port', '-P', type=int, action='store',
                        dest='port', nargs='?', default=8888,
                        help='the port on which the server is listening')
    parser.add_argument('--packetsize', '-N', type=int, action='store',
                        nargs='?', default=1000, help='How many samples a '
                        'packet will contain')
    parser.add_argument('--bandwidth', '-B', type=float, action='store',
                        nargs='?', default=1000000.0, help='Simulation '
                        'bandwidth')
    parser.add_argument('--centerfreq', '-F', type=float, action='store',
                        nargs='?', default=100000000.0, help='Center frequency'
                        ' of simulation band')

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
    # turn the hw model parameters in a dictionary
    if args.hwopts is not None:
        args.hwopts = dict(zip(args.hwopts[0::2], args.hwopts[1::2]))
        for key in args.hwopts.keys():
            # convert the parameters to float, except if the parameter is a
            #string than float() will throw a value error and we don't have to
            #do anything
            try:
                args.hwopts[key] = float(args.hwopts[key])
            except ValueError:
                pass
    else:
        args.hwopts = {}
    hw_model = hw_models[args.hwmodel]

    reactor.listenTCP(args.port, winelo.server.SyncFactory(args, channel_model, hw_model))
    print "Server is listening on port %d" % (args.port)
    print "The initial packet size is %i" % (args.packetsize)
    reactor.run()

if __name__ == '__main__':
    main()
