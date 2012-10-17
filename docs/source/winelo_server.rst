Server
******

.. automodule:: winelo.server
        :members:

Usually you should never have to deal with this module.
If you want to run a winelo server just execute **apps/server.py**::

        ./server.py --help
        linux; GNU C++ version 4.6.3; Boost_104601; UHD_003.004.003-232-g390752c6

        usage: server.py [-h] [--model [MODEL]] [--opts [OPTS [OPTS ...]]]
                         [--port [PORT]] [--packetsize [PACKETSIZE]]

        Starts the gnuradio-channel-simmulation server GRCSS.

        optional arguments:
          -h, --help            show this help message and exit
          --model [MODEL], -M [MODEL]
                                name of the channel model to be used. Available models are:
                                cs_meas
                                const
                                rayleigh
                                cost207hillyterrain
                                cost207typicalurban
                                cost207badurban
                                cost207ruralarea
          --opts [OPTS [OPTS ...]], -O [OPTS [OPTS ...]]
                                channel model parameters. Something like:
                                [sample_rate 32000 fmax 100] or [k 1]
          --port [PORT], -P [PORT]
                                the port on which the server is listening
          --packetsize [PACKETSIZE], -N [PACKETSIZE]
                                How many samples a package will contain

The models are GNU Radio blocks from :mod:`winelo.channel.models.cs_meas_cc`, :mod:`winelo.channel.models.rayleigh_cc`,
:mod:`winelo.channel.models.cost207` or the standard gnuradio library.
They are stored in a Python dictionary and are accessed via their respective keys.
With **opts** parameters are passed to the GNU Radio model block.
The rest of the arguments should be self-explanatory.
For example, if a rayleigh channel is to be modelled, we start the server with the following command:::

        ./server --model rayleigh --opts [sample_rate 32000 fmax 100]

GNU Radio Server flowgraph
==========================
.. automodule:: winelo.server.grchannel
        :members:

Twisted Interface
=================

.. automodule:: winelo.server.tw2gr_c
        :members:

.. automodule:: winelo.server.gr2tw_c
        :members:
