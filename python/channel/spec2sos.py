#!/usr/bin/python
import numpy as np

class spec2sos():
    """
    The Sum-of-Sinusoids method can only be used for symmetric doppler spectra.
    See Paetzold p. 104.
    """
    def __init__(self, N=10, dopplerspec='jakes', method='mea'):
        self.N = N
        self.sos = {}
        if dopplerspec is 'jakes':
            print 'Generating Jakes spectrum'
            self.psd = self.jakes()
        self.methodhandler = {
                'med':self.med,
                'mea':self.mea
                }
        print 'method: ', method
        self.methodhandler[method]()

    def jakes(self, fmax = 100, sigma=1):
        N = 2*fmax+1
        psd = np.zeros( N )
        freqs = np.linspace(-fmax,fmax,N)
        comp_jakes = lambda f: sigma**2/(np.pi*fmax*np.sqrt( 1 - (f/fmax)**2))
        psd[1:-1] = comp_jakes( freqs[1:-1] )
        return (freqs, psd)

    # Method of Equal Distance. Paetzold p 151
    def med(self):
        N = self.N
        fstart = 0
        fend = max(self.psd[0])
        # initial bins
        freqs_sos = np.linspace(fstart, fend, N+1)
        # space between two bins
        delta_f = freqs_sos[1] - freqs_sos[0]
        # shift all bins half of an interval to the right
        freqs_sos = freqs_sos + delta_f/2
        # delete the last entry
        freqs_sos = freqs_sos[:-1]
        # initialize the Sum-of-Sinusoid power spectrum density
        psd_sos = np.zeros( freqs_sos.shape )

        for idx, f in enumerate(freqs_sos):
            idx_temp = np.logical_and( self.psd[0] >= f-delta_f/2, self.psd[0] <= f+delta_f/2 )
            freqs_temp = self.psd[0][idx_temp]
            psd_temp = self.psd[1][idx_temp]
            psd_sos[idx] = np.trapz( psd_temp, freqs_temp )

        print 'The following to values can be used to judge the quality of the approximation'
        print 'np.trapz(psd, freqs): ', np.trapz(self.psd[1], self.psd[0])
        print '2*sum(psd_sos): ', 2*sum(psd_sos)

        self.sos = zip(freqs_sos, 2*psd_sos )

    # Method of Equal Areas, Paetzold p 162
    def mea(self):
        G = np.cumsum(self.psd[1])
        sigma_squared = G[-1]
        n_bin = np.arange(1, self.N + 1, dtype=float)
        n_bin = sigma_squared/2*(1 + n_bin/len(n_bin))
        freqs_sos = np.zeros( self.N )
        for idx, n in enumerate(n_bin):
            min_dist = min( np.abs(G - n) )
            index = np.where( (np.abs(G - n) - min_dist) == 0)[0][0]
            freqs_sos[idx] = self.psd[0][index]
        coeffs = np.array( [2*np.sqrt(sigma_squared)]*self.N)
        self.sos = zip(freqs_sos, coeffs)

    def get_sos(self):
        return self.sos

    def plot_spectra(self):
        import pylab as plt
        h = plt.plot(self.psd[0], self.psd[1])
        freqs = [ el[0] for el in self.sos ]
        ampls = [ el[1] for el in self.sos ]
        plt.stem(freqs, ampls)
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()

