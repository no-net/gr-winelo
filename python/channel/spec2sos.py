#!/usr/bin/python
import numpy as np

class spec2sos():
    """
    The Sum-of-Sinusoids method can only be used for symmetric doppler spectra.
    See Paetzold p. 104.

    Parameters
    ----------

    psd: tuple( freqs, spectrum )
        power spectrum density as produced by the cost207 module
    N : int
        number of sinusoids
    method : string
        method used to compute gains and frequencies
        med: method of equal distances
        mea: method of equal area

    """

    def __init__(self, psd, N=10, method='mea'):
        self.N = N
        self.sos = {}
        self.psd = psd
        self.methodhandler = {
                'med':self.med,
                'mea':self.mea
                }
        self.methodhandler[method]()

    # Method of Equal Distances. Paetzold p 151
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
        coeffs = np.zeros( freqs_sos.shape )

        for idx, f in enumerate(freqs_sos):
            idx_temp = np.logical_and( self.psd[0] >= f-delta_f/2, self.psd[0] <= f+delta_f/2 )
            freqs_temp = self.psd[0][idx_temp]
            coeff_temp = self.psd[1][idx_temp]
            coeffs[idx] = np.trapz( coeff_temp, freqs_temp )

        coeffs = np.divide( coeffs, np.sum(coeffs) )
        self.sos = zip(freqs_sos, coeffs )

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
        # normalize to one
        coeffs = np.divide( coeffs, np.sum(coeffs) )
        self.sos = zip(freqs_sos, coeffs)

    def get_sos(self):
        return self.sos

    def plot_spectra(self):
        import pylab as plt
        freqs = [ f[0] for f in self.sos ]
        negfreqs = [ -f[0] for f in self.sos ]
        # convert the amplitudes of the sinusoids to a psd
        ampls = [ (a[1]/2)**2 for a in self.sos ]
        plt.stem(freqs, ampls)
        plt.stem(negfreqs, ampls)
        plt.xlim(1.5*negfreqs[-1], 1.5*freqs[-1] )
        plt.ylim(0, 1.5*max(ampls))
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$\| S(f) \|$')
        plt.show()

