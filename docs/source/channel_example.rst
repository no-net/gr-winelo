Example
+++++++
The easiest way to get a complex Gaussian process is to use the corresponding Block that comes with **gr-winelo**.
The block is also available in GNU Radio companion in the category its parameters are the following.
First we create an instance of a COST 207 model::

	from winelo.channel.models import cost207
	myspecs = cost207.dopplerspecs(N = 2001, fmax = 100)
	gauss1 = myspecs.get_gauss1()

where *N* is the number of points where the Doppler spectra are evaluated and *fmax* is the maximum Doppler shift.
The various spectra can then be extracted with the *get_gauss1*, *get_gauss2*, *get_jakes* and *get_rice* methods.
They return a tuple which contains two Numpy arrays: a $N \times 1$ array containing frequencies that are evenly spread from *-fmax* and *fmax*, and also a FIXME N \times 1 array which contains the power of the Doppler spectrum at these frequencies.

If we now wish to turn this Doppler spectrum into a sum of sinusoids or cisoids the corresponding libraries have to be loaded.
Since the Gauss1 spectrum of the COST 207 model is uneven, we will be using the sum of cisoids approach.::

	from winelo.channel import spec2soc
	gauss1_soc = spec2soc( gauss1, N=10, method='gmea')

here *N* is the number of cisoids that we want to use, and *gmea* stands for generalized methods of equal areas which is used to compute the frequencies and amplitudes of the cisoids, given the spectrum *gauss1*.

Let's have a look at our sum of cisoids and how it relates to the Doppler spectrum supplied by the COST 207 methods::

	gauss1_soc.plot_spectra()

which gives us the following plot:

.. figure::  images/soc_and_spec.png
        :align:   center
        :scale: 50

	Sum of Cisoids and its spectrum

we can get the actual sum of cisoids with the method *gauss1_soc.get_soc()*, which returns a list of *N* tuple, where each tuple is a pair of the frequency and the amplitude of one cisoid.
