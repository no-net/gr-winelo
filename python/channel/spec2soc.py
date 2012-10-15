import numpy as np

class spec2soc():
    """
    The Sum-of-Cisoids method is better suited for non-symmetric Doppler
    Spectra. Paetzold p126
    """
    def __init__(self, spec, N=10, method='gmea'):
        """
        Parameters:

        spec: tuple( freqs, spectrum )
            power spectrum density as produced by the cost207 module
        N : int
            number of sinusoids
        method : string
            method used to compute gains and frequencies
            med: method of equal distances
            mea: method of equal area

        """
        self.N = N
        self.spec = spec
        self.methodhandler = {
                'gmea':self.gmea,
                'med':self.med
                }
        self.methodhandler[method]()

    def gmea(self):
        """ General Method of Equal Areas, [paetzold2011mobile]_ p. 225.
        """
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

    def med(self):
        """ Method of Equal Distances [paetzold2011mobile]_ p. 151.
        The method of equal distances is only described for sum of sinusoids but I think it is
        also applicable to the sum of cisoids approach.

        """
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

