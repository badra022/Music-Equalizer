from PyQt5 import QtCore
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import rfft, rfftfreq, irfft
from IPython.display import Audio
from scipy.io import wavfile
from scipy.io.wavfile import write
from librosa import display
from spectrogram import my_specgram
import winsound
class signal(object):
    timer = QtCore.QTimer()
    speedFactor = 3000

    def __init__(self, data, fs, widget):
        self.amplitude = np.int32((data))
        self.fs = fs
        self.fmax = fs/2
        self.maxAmplitude = self.amplitude.max()
        self.minAmplitude = self.amplitude.min()
        self.zoomFactor = 1
        self.__class__.speedFactor = fs/10
        self.time = np.linspace(0., len(data)/fs, len(data))
        self.startTimeIdx = 0
        self.endTimeIdx = int(fs * self.zoomFactor) - 1
        self.__class__.timer.setInterval(200) # m     interval
        self.widget = widget
        self.plot()
        self.save()
        # self.listen()
        
    def plot(self):
        self.maxAmplitude = self.amplitude.max()
        self.minAmplitude = self.amplitude.min()
        self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        # self.widget.setYRange(-32767 * self.zoomFactor , 32767 * self.zoomFactor)
        self.widget.setYRange(self.minAmplitude * self.zoomFactor , self.maxAmplitude * self.zoomFactor)
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.widget.clear()
        self.widget.plot(self.time, self.amplitude, pen=self.pen)

    def moveGraph(self):
        if len(self.time) - int(self.fs * self.zoomFactor):
            # self.maxAmplitude = max(self.amplitude[self.startTimeIdx:self.endTimeIdx])
            # self.minAmplitude = min(self.amplitude[self.startTimeIdx:self.endTimeIdx])
            # self.widget.setYRange(self.minAmplitude * self.zoomFactor , self.maxAmplitude * self.zoomFactor)
            self.startTimeIdx = int(self.startTimeIdx + self.__class__.speedFactor) % (len(self.time) - int(self.fs * self.zoomFactor))
            self.endTimeIdx = int(self.endTimeIdx + self.__class__.speedFactor % len(self.time)) - 1
            self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])

    def scrollSignal(self, value):
        if len(self.time) - int(self.fs * self.zoomFactor):
            # value: 0 -> 100
            self.startTimeIdx = int(value/100* (len(self.amplitude) - int(self.fs * self.zoomFactor - 1)))
            self.endTimeIdx = int(self.startTimeIdx + int(self.fs * self.zoomFactor - 1))
            self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])

    def zoomIn(self):
        if self.zoomFactor >= 0.2:
            self.zoomFactor = self.zoomFactor - 0.1
            self.adjustGraph()
    def zoomOut(self):
        if self.zoomFactor < 2.0:
            self.zoomFactor = self.zoomFactor + 0.1
            self.adjustGraph()
            
    def adjustGraph(self):
        self.endTimeIdx = int(self.startTimeIdx + int(self.fs * self.zoomFactor))
        self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        self.widget.setYRange(self.minAmplitude * self.zoomFactor , self.maxAmplitude * self.zoomFactor)
        
    def getFigure(self):
        fig = plt.figure(figsize=(10, 5))
        plt.plot(self.time,self.amplitude)
        plt.xlabel('time (sec)')
        plt.ylabel('amplitude (mv)')
        return fig
    
    def getFourierFigure(self):
        pass
    
    def getSpectrogram(self, minfreq, maxfreq, cmap):
        fig = plt.figure(figsize=(10, 5))
        powerSpectrum, freqenciesFound, time, _ = my_specgram(self.amplitude, Fs=self.fs,
         cmap=cmap, maxfreq=maxfreq, minfreq=minfreq)
        plt.pcolormesh(time, freqenciesFound, powerSpectrum, cmap=cmap)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.colorbar()
        return fig

    def plotSpectrogram(self, cmap, minfreq, maxfreq, imageItem, hist):
        # 
        powerSpectrum, freqenciesFound, time, _ = my_specgram(self.amplitude[int(self.startTimeIdx) : int(self.endTimeIdx)],
         Fs=self.fs, cmap=cmap, maxfreq=maxfreq, minfreq=minfreq)
        # for more colormaps: https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(np.min(powerSpectrum), np.max(powerSpectrum))
        # Sxx contains the amplitude for each pixel
        imageItem.setImage(powerSpectrum)
        return powerSpectrum, time, freqenciesFound

    def listen(self):
        winsound.PlaySound("output_sound.wav", winsound.SND_ASYNC)
    def save(self):
        write("output_sound.wav", self.fs, self.amplitude.astype(np.int16))