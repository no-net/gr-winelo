import numpy

def hwemu(samples, profile):
    samples = awgn(samples, profile['noise_ampl'])

    samples, profile['phase_noise_hist'] = phaseNoise(samples,
                                            profile['phase_noise_ampl'],
                                            profile['phase_noise_hist'])

    samples, profile['cur_phase'] = freqOffset(samples,
                                        profile['cur_phase'],
                                        profile['freq_offset'])

    samples = iqImbalance(samples,
            profile['inphase_ampl'],
            profile['quadrature_ampl'])

    return samples, profile


def awgn(samples, ampl):
    """
    Adds Gaussian noise to the clients samples
    """
    len_samples = len(samples)
    inoise = ampl*numpy.random.randn(len_samples)
    qnoise = ampl*numpy.random.randn(len_samples)
    noise = inoise + 1j*qnoise
    return samples + noise

def freqOffset(samples, current_phase, f):
    """
    Simulates a frequency offset between the transmitter and the receiver
    """
    phi = current_phase
    f = f
    tmax = len(samples)
    phase_mod = numpy.array( [ phi*(numpy.exp(1j*f*t)) for t in range(tmax) ] )
    samples = numpy.multiply( samples, phase_mod )
    # set the current phase for the next package
    phi = phase_mod[-1]*numpy.exp(1j*f)
    return samples, phi

def phaseNoise(samples, ampl, phase_noise_hist):
    """
    Simulates phase noise. The phase noise is correlated by a single-pole
    IIR-Filter. This is the identical approach Matt Ettus used for his
    generic blocks for his presentation "Reality Bites... Why doesn't my
    signal look like the textbook?"
    """
    tmax = len(samples)
    phase_noise = numpy.exp(1j*ampl*numpy.random.randn(tmax))
    # IIR-Filter which is used to correlate the various phase-noise samples
    alpha = 0.1
    for idx, val in enumerate(phase_noise):
        phase_noise[idx] = val + alpha*phase_noise_hist
        phase_noise[idx] /= numpy.abs(phase_noise[idx])
        phase_noise_hist = phase_noise[idx]
    return numpy.multiply( samples, phase_noise ), phase_noise_hist

def iqImbalance(samples, i_ampl, q_ampl):
    """
    Simulates IQ imbalance
    """
    return i_ampl*samples.real + q_ampl*1j*samples.imag
