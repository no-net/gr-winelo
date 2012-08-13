#!/usr/bin/python
import numpy as np

class spec2soc():
    """
    The Sum-of-Sinusoids method can only be used for symmetric doppler spectra.
    See Paetzold p. 104.
    """
    def __init__(self, spec, N=20, method='gmea'):
        self.N = N
        self.spec = spec
        self.methodhandler = {
                'gmea':self.gmea
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
        coeffs = np.array( [np.sqrt(sigma_squared/self.N)]*self.N)
        self.soc = zip(freqs_soc, coeffs)

    def get_soc(self):
        print self.soc
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

