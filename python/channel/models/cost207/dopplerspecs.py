import numpy as np

class dopplerspecs():
    """ Computes the Doppler spectra defined by the COST207 model.
    """

    def __init__(self, N, fmax):
        """ Parameters:

        N : int
            size of the spectrum array that is returned
        fmax : int, float
            maximum Doppler frequency

        """

        self.N = N
        self.fmax = fmax
        self.A_1 = 50/( np.sqrt( 2*np.pi ) * 3 * self.fmax )
        self.A_2 = 10**1.5/( np.sqrt( 2*np.pi ) * (np.sqrt(10) + 5) * self.fmax )
        self.freqs = np.linspace( -self.fmax, self.fmax, self.N)

        self.specs_odd = ['gauss1', 'gauss2', 'rice']
        self.specs_even = ['jakes']


    def _gauss(self, A_i, f_i, s_i, f):
        return A_i*np.exp( (-(f-f_i)**2) / (2*s_i**2) )

    def _gen_jakes(self):
        sigma = 1
        psd = np.zeros(self.N)
        comp_jakes = lambda f: sigma**2/(np.pi*self.fmax*np.sqrt( 1 - (f/self.fmax)**2))
        psd[1:-1] = comp_jakes( self.freqs[1:-1] )
        return psd

    def _gen_gauss1(self):
        A_1 = self.A_1
        f_1 = -0.8*self.fmax
        s_1 = 0.05*self.fmax

        A_2 = self.A_1/10
        f_2 = 0.4*self.fmax
        s_2 = 0.1*self.fmax

        psd = self._gauss(A_1, f_1, s_1, self.freqs) + self._gauss(A_2, f_2, s_2, self.freqs)
        return psd

    def _gen_gauss2(self):
        A_1 = self.A_2
        f_1 = 0.7*self.fmax
        s_1 = 0.1*self.fmax

        A_2 = self.A_2/10**1.5
        f_2 = -0.4*self.fmax
        s_2 = 0.15*self.fmax

        psd = self._gauss(A_1, f_1, s_1, self.freqs) + self._gauss(A_2, f_2, s_2, self.freqs)
        return psd

    def _gen_rice(self):
        sigma = 0.41
        psd = np.zeros(self.N)
        comp_jakes = lambda f: sigma**2/(np.pi*self.fmax*np.sqrt( 1 - (f/self.fmax)**2))
        psd[1:-1] = comp_jakes( self.freqs[1:-1] )
        f_dirac = np.int(0.7*self.N)
        psd[f_dirac] = psd[f_dirac] + 0.91**2
        return psd

    def get_jakes(self):
        """ Returns the Jakes PSD. """
        return (self.freqs, self._gen_jakes() )

    def get_gauss1(self):
        """ Returns the Gauss 1 PSD. """
        return (self.freqs, self._gen_gauss1() )

    def get_gauss2(self):
        """ Returns the Gauss 2 PSD. """
        return (self.freqs, self._gen_gauss2() )

    def get_rice(self):
        """ Returns the Rice PSD. """
        return (self.freqs, self._gen_rice() )

    def plot_jakes(self):
        """ Plots the Jakes PSD. """
        import pylab as plt
        plt.plot(self.freqs, self._gen_jakes())
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()

    def plot_gauss1(self):
        """ Plots the Gauss 1 PSD. """
        import pylab as plt
        plt.plot(self.freqs, self._gen_gauss1())
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()

    def plot_gauss2(self):
        """ Plots the Gauss 2 PSD. """
        import pylab as plt
        plt.plot(self.freqs, self._gen_gauss2())
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()

    def plot_rice(self):
        """ Plots the Rice PSD. """
        import pylab as plt
        plt.plot(self.freqs, self._gen_rice())
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()
