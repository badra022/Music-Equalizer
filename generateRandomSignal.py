import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

frequences=[3000,1100,1500,800,2000,2600,1030,2005,1000,5500]
fs=2* max(frequences)

x=np.arange(fs)
signal=0
amplitudes=[2000,5550,1000,3360,988,100,7888,6000,1100,8700]

j=0
for i in range(len (frequences)):
    y1=np.sin(2*np.pi*frequences[i]*(x/fs))
    signal=signal+amplitudes[j]*y1
    j=j+1

t = np.linspace(0., 1., fs)
write("generated.wav", fs, signal.astype(np.int16))

total_ts_sec = len(signal)/fs
print("The total time series length = {} sec (N points = {}) ".format(total_ts_sec, len(signal)))
plt.figure(figsize=(20,3))
plt.plot(signal)
plt.xticks(np.arange(0,len(signal),fs),
        np.arange(0,len(signal)/fs,1))
plt.ylabel("Amplitude")
plt.xlabel("Time (second)")
plt.show()