#!/usr/bin/python
import numpy as np

class spec2soc():
    """
    The Sum-of-Sinusoids method can only be used for symmetric doppler spectra.
    See Paetzold p. 104.
    """
    def __init__(self, spec, N=10, method='gmea'):
        self.N = N
        self.spec = spec
        self.methodhandler = {
                'gmea':self.gmea,
                'med':self.med
                }
        self.methodhandler[method]()

    # General Method of Equal Areas, Paetzold p 225
    def gmea(self):
        P_S = np.cumsum(self.spec[1])
        # sigma squared is equal to the integral over the Doppler spectrum.
        # Therefor it is also equal to the last element of the cumulative sum
        sigma_squared = P_S[-1]
        n_bin = np.arange(1, self.N + 1, dtype=float)
        n_bin = sigma_squared * (self.N - n_bin + 1/np.float(2))
        n_bin = n_bin / np.float(self.N)
        freqs_soc = np.zeros( self.N )
        for idx, n in enumerate(n_bin):
            min_dist = min( np.abs(P_S - n) )
            index = np.where( (np.abs(P_S - n) - min_dist) == 0)[0][0]
            freqs_soc[idx] = self.spec[0][index]
        # normalize to power of one
        spec_soc = np.array( [float(1)/self.N]*self.N)
        self.soc = zip(freqs_soc, spec_soc)

    # Method of Equal Distance. Paetzold p 151
    # in Paetzold it is only described for sum of sinusoids but I think it is
    # also applicable to sum of cisoids
    def med(self):
        N = self.N
        fstart = min(self.spec[0])
        fend = max(self.spec[0])
        # initial bins
        freqs_soc = np.linspace(fstart, fend, N+1)
        # space between two bins
        delta_f = freqs_soc[1] - freqs_soc[0]
        # shift all bins half of an interval to the right
        freqs_soc = freqs_soc + delta_f/2
        # delete the last entry
        freqs_soc = freqs_soc[:-1]
        # initialize the Sum-of-Sinusoid power spectrum density
        spec_soc = np.zeros( freqs_soc.shape )

        for idx, f in enumerate(freqs_soc):
            idx_temp = np.logical_and( self.spec[0] >= f-delta_f/2, self.spec[0] <= f+delta_f/2 )
            freqs_temp = self.spec[0][idx_temp]
            spec_temp = self.spec[1][idx_temp]
            spec_soc[idx] = np.trapz( spec_temp, freqs_temp )

        print 'The following to values can be used to judge the quality of the approximation'
        print 'np.trapz(psd, freqs): ', np.trapz(self.spec[1], self.spec[0])
        print 'sum(spec_soc): ', sum(spec_soc)

        self.soc = zip(freqs_soc, spec_soc)

    def get_soc(self):
        return self.soc

    def plot_spectra(self):
        import pylab as plt
        h = plt.plot(self.spec[0], self.spec[1])
        freqs = [ el[0] for el in self.soc ]
        ampls = [ el[1] for el in self.soc ]
        plt.stem(freqs, ampls)
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()

