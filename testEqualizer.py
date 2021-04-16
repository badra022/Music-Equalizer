from librosa import display
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq, irfft
from IPython.display import Audio
from scipy.io import wavfile
from scipy.io.wavfile import write
import cmath
from spectrogram import my_specgram

fig, axs = plt.subplots(2, 2)

# reading the .wav file and normalizing the data
samplerate, data = wavfile.read('generated.wav')
total_ts_sec = len(data)/samplerate
print("sampling frequency of the input wav: " ,samplerate)
print("The total time series length = {} sec (N points = {}) ".format(total_ts_sec, len(data)))
# data_normalized = np.int16((data / data.max()) * 32767)
axs[0,0].plot(data)
plt.xticks(np.arange(0,int(total_ts_sec),int(total_ts_sec)))

# Number of samples in normalized_tone
N = len(data)

# getting fft of the signal and subtracting amplitudes and phases
rfft_coeff = rfft(data)
signal_rfft_Coeff_abs = np.abs(rfft_coeff)
signal_rfft_Coeff_angle = np.angle(rfft_coeff)

# getting frequencies in range 0 to fmax to access each coeff of rfft coefficients
frequencies = rfftfreq(N, 1 / samplerate)

# The maximum frequency is half the sample rate
# points_per_freq = len(frequencies) / (samplerate / 2)

axs[1,0].plot(frequencies, signal_rfft_Coeff_abs)

# filter that multiply frequency band (from low to high) by factor
def processFrequencyBand(low, high, factor):
    # The maximum frequency is half the sample rate
    points_per_freq = len(frequencies) / (samplerate / 2)
    for f in frequencies:
        if low < f < high:
            f_idx = int(points_per_freq * f)
            signal_rfft_Coeff_abs[f_idx] = signal_rfft_Coeff_abs[f_idx] * factor
        else:
            pass

# processing the signal
processFrequencyBand(1000, 2000, 5)

axs[1,1].plot(frequencies, signal_rfft_Coeff_abs)

# The maximum frequency is half the sample rate
points_per_freq = len(frequencies) / (samplerate / 2)

# constructing fft coefficients again (from amplitudes and phases) after processing the amplitudes
new_rfft_coeff = np.zeros((len(frequencies),), dtype=complex)
for f in frequencies:
    try:
        f_idx = int(points_per_freq * f)
        new_rfft_coeff[f_idx]= signal_rfft_Coeff_abs[f_idx]*cmath.exp(1j * signal_rfft_Coeff_angle[f_idx])
    except:
        pass

# constructing the new signal from the fft coeffs by inverse fft
new_sig = irfft(new_rfft_coeff)

axs[0,1].plot(new_sig)
plt.xticks(np.arange(0,int(total_ts_sec),int(total_ts_sec)))
plt.show()

# plotting spectrogram for the original signal
powerSpectrum, freqenciesFound, time, imageAxis = my_specgram(data, Fs=samplerate, cmap='plasma')#, maxfreq=2000, minfreq=1000)
print(imageAxis)

# Plotting with Matplotlib in comparison
plt.pcolormesh(time, freqenciesFound, powerSpectrum, cmap='plasma')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.colorbar()

plt.show()


# plotting spectrogram for the new signal
powerSpectrum, freqenciesFound, time, imageAxis = my_specgram(new_sig, Fs=samplerate, cmap='plasma')#, maxfreq=2000, minfreq=1000)
# for more colormaps: https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html

# Plotting with Matplotlib in comparison
plt.pcolormesh(time, freqenciesFound, powerSpectrum, cmap='plasma')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.colorbar()
plt.show()


# save the new signal to a wav file for further processing!
write("generated_new.wav", samplerate, new_sig.astype(np.int16))
