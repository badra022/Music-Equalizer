import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq, irfft
import cmath

def processFrequencyBand(data, fs,factors):
    # Number of samples in signal
    N = len(data)

    # getting fft of the signal and subtracting amplitudes and phases
    rfft_coeff = rfft(data)
    signal_rfft_Coeff_abs = np.abs(rfft_coeff)
    signal_rfft_Coeff_angle = np.angle(rfft_coeff)

    # getting frequencies in range 0 to fmax to access each coeff of rfft coefficients
    frequencies = rfftfreq(N, 1 / fs)
    # plt.plot(frequencies, signal_rfft_Coeff_abs)
    # plt.show()
    
    # The maximum frequency is half the sample rate
    points_per_freq = len(frequencies) / (fs / 2)
    
    for idx in range(len(factors)):
        low = ((fs / 2)/len(factors)) * idx
        # print("low: ",low)
        high = (((fs / 2)/len(factors)) * (idx + 1)) - 1
        # print("high: ",high)

        # filter that multiply frequency band (from low to high) by factor
        for f in frequencies:
            if low < f < high:
                f_idx = int(points_per_freq * f)
                signal_rfft_Coeff_abs[f_idx] = signal_rfft_Coeff_abs[f_idx] * factors[idx]
            else:
                pass

    # plt.plot(frequencies, signal_rfft_Coeff_abs)    
    # plt.show()
    # constructing fft coefficients again (from amplitudes and phases) after processing the amplitudes
    new_rfft_coeff = np.zeros((len(frequencies),), dtype=complex)
    for f in frequencies:
        try:
            f_idx = int(points_per_freq * f)
            new_rfft_coeff[f_idx]= signal_rfft_Coeff_abs[f_idx]*cmath.exp(1j * signal_rfft_Coeff_angle[f_idx])
        except:
            pass

    # constructing the new signal from the fft coeffs by inverse fft
    return irfft(new_rfft_coeff)