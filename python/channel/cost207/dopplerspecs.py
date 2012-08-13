#!/usr/bin/python
import numpy as np

class dopplerspecs():
    def __init__(self, N, fmax):
        self.N = N
        self.fmax = fmax
        self.A_1 = 50/( np.sqrt( 2*np.pi ) * 3 * self.fmax )
        self.A_2 = 10**1.5/( np.sqrt( 2*np.pi ) * (np.sqrt(10) + 5) * self.fmax )
        self.gen_spec = {
                'jakes': self.jakes,
                'gauss1': self.gauss1,
                'gauss2': self.gauss2,
                'rice': self.rice
                }

        self.spectra = {'jakes':None,
                        'gauss1':None,
                        'gauss2':None,
                        'rice':None }
        for key in self.spectra.keys():
            print "Generating %s Doppler spectrum" % key
            self.spectra[key] = self.gen_spec[key]()

    def _gauss(self, A_i, f_i, s_i, f):
        return A_i*np.exp( (-(f-f_i)**2) / (2*s_i**2) )

    def jakes(self):
        fmax = self.fmax
        N = self.N
        sigma = 1
        psd = np.zeros(N)
        freqs = np.linspace(-fmax, fmax, N)
        comp_jakes = lambda f: sigma**2/(np.pi*fmax*np.sqrt( 1 - (f/fmax)**2))
        psd[1:-1] = comp_jakes( freqs[1:-1] )
        return psd

    def gauss1(self):
        fmax = self.fmax
        N = self.N
        freqs = np.linspace(-fmax, fmax, N)

        A_1 = self.A_1
        f_1 = -0.8*fmax
        s_1 = 0.05*fmax

        A_2 = self.A_1/10
        f_2 = 0.4*fmax
        s_2 = 0.1*fmax

        psd = self._gauss(A_1, f_1, s_1, freqs) + self._gauss(A_2, f_2, s_2, freqs)
        return psd

    def gauss2(self):
        fmax = self.fmax
        N = self.N
        freqs = np.linspace(-fmax, fmax, N)

        A_1 = self.A_2
        f_1 = 0.7*fmax
        s_1 = 0.1*fmax

        A_2 = self.A_2/10**1.5
        f_2 = -0.4*fmax
        s_2 = 0.15*fmax

        psd = self._gauss(A_1, f_1, s_1, freqs) + self._gauss(A_2, f_2, s_2, freqs)
        return psd

    def rice(self):
        fmax = self.fmax
        N = self.N
        sigma = 0.41
        psd = np.zeros(N)
        freqs = np.linspace(-fmax, fmax, N)
        comp_jakes = lambda f: sigma**2/(np.pi*fmax*np.sqrt( 1 - (f/fmax)**2))
        psd[1:-1] = comp_jakes( freqs[1:-1] )
        f_dirac = np.int(0.7*N)
        psd[f_dirac] = psd[f_dirac] + 0.91**2
        return psd

    def get_spec(self, spec):
        return ( np.linspace( -self.fmax, self.fmax, self.N), self.spectra[spec] )

    def plot_spec(self, spec):
        import pylab as plt
        plt.plot(self.spectra[spec])
        plt.xlabel(r'$f$ in Hz')
        plt.ylabel(r'$S(f)$')
        plt.show()
