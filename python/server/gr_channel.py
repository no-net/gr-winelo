from gnuradio import gr, analog
import time

class gr_channel():
    """ Models the radio channel between all transmitters and receivers.
    """

    def __init__(self, txs, rxs):
        self.tb = gr.top_block()
        # the lists of the connected clients are called by references
        self.txs = txs
        self.rxs = rxs

    def teardown_channel(self):
        """ Tears down the channel after a client connected or disconnected.
        """
        tb = self.tb
        tb.stop()
        print 'GNU Radio flowgraph stopped'
        for tx in self.txs:
            print 'setting kill flag'
            tx.kill = True
            tx.condition.acquire()
            tx.condition.notify()
            tx.condition.release()
            #print "DEBUG: Condition released"
        tb.wait()
        print 'GNU Radio flowgraph waited'
        tb.disconnect_all()
        print 'All connections between blocks were dissolved'
        for tx in self.txs:
            print 'clearing kill flag'
            tx.kill = False

    def rebuild_channel(self):
        """ Rebuilds the channel after it was torn down.
        """

        tb = self.tb
        rxs = self.rxs
        txs = self.txs

        print 'Rebuilding the GNU Radio Channel'
        print 'Transmitters:', txs
        print 'Receivers:', rxs
        adders = []
        for i in range(len(rxs)):
            adders.append( gr.add_cc() )
        print 'Adders:', adders
        # The two following for loops built a structure similar to this,
        # depending on the number of transmitters and receivers
        #
        #                    +--------+           +-------+
        #           -------->| H(1,1) |---------->|       |
        # +------+  |        +--------+           |       |      +------+
        # | Tx 1 |---                             | Adder |----->| Rx 1 |
        # +------+  |        +--------+           |       |      +------+
        #           |  ----->| H(1,2) |---------->|       |
        #           |  |     +--------+           +-------+
        #           |  |
        #           |  |     +--------+           +-------+
        #           ---+---->| H(2,1) |---------->|       |
        # +------+     |     +--------+           |       |      +------+
        # | Tx 2 |------                          | Adder |----->| Rx 2 |
        # +------+     |     +--------+           |       |      +------+
        #              ----->| H(2,2) |---------->|       |
        #                    +--------+           +-------+
        #
        for rx_idx, rx in enumerate(rxs):
            print
            print 'Making connections for %s' % rx.info['name']
            for tx_idx, tx in enumerate(txs):
                print '==> Connecting source of %s to its channel' % tx.info['name']
                tb.connect(tx.info['block'], tx.info['channels'][rx.info['name']])
                print '==> Connecting this channel to the adder at port %d' % tx_idx
                tb.connect(tx.info['channels'][rx.info['name']], (adders[rx_idx], tx_idx))
                print
            # check if the list txs is not empty
            if txs:
                print 'Connecting the adder to the receiver %s' % rx.info['name']
                tb.connect(adders[rx_idx], rx.info['block'])

        print 'restarting gnuradio flowgraph'
        tb.start()
