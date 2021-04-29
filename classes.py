from PyQt5 import QtCore
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import write
import winsound
import math

midColor = [(0, 182, 188, 255), (128, 128, 128, 255),  (0, 128, 128, 255), (230,0,115, 255), (204, 0, 0, 255)]
maxColor = [(246, 111, 0, 255), (0, 0, 0, 255), (230, 230, 0, 255), (0,0,0, 255), (0, 0, 0, 255)]
minColor = [(75, 0, 113, 255), (255, 255, 255, 255), (102, 0, 34, 255), (255,255,255, 255), (255,255,255, 255)]

class signal(object):
    timer = QtCore.QTimer()
    speedFactor = 3000

    def __init__(self, data, fs, widget, winNumber):
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
        self.winNumber = winNumber
        self.plot()
        self.listen()

    def updateSignal(self, data):
        self.amplitude = np.int32((data))
        self.time = np.linspace(0., len(data)/self.fs, len(data))
        self.plot()
        self.save()
        self.listen()

    def plot(self):
        self.maxAmplitude = self.amplitude.max()
        self.minAmplitude = self.amplitude.min()
        self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        self.widget.setYRange(self.minAmplitude * self.zoomFactor , self.maxAmplitude * self.zoomFactor)
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.widget.clear()
        self.widget.plot(self.time, self.amplitude, pen=self.pen)

    def moveGraph(self):
        if len(self.time) - int(self.fs * self.zoomFactor):
            self.startTimeIdx = int(self.startTimeIdx + self.__class__.speedFactor) % (len(self.time) - int(self.fs * self.zoomFactor))
            self.endTimeIdx = int(self.endTimeIdx + self.__class__.speedFactor % len(self.time)) - 1
            self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])

    def scrollSignal(self, value): # value: 0 -> 100
        if len(self.time) - int(self.fs * self.zoomFactor):
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
        self.endTimeIdx = int(self.startTimeIdx + int(self.fs * self.zoomFactor - 1))
        self.widget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        self.widget.setYRange(self.minAmplitude * self.zoomFactor , self.maxAmplitude * self.zoomFactor)

    def getFigure(self):
        fig = plt.figure(figsize=(10, 5))
        plt.plot(self.time[self.startTimeIdx:self.endTimeIdx],self.amplitude[self.startTimeIdx:self.endTimeIdx])
        plt.xlabel('time (sec)')
        plt.ylabel('amplitude (mv)')
        return fig

    def getSpectrogram(self, cmap):
        fig = plt.figure(figsize=(10, 5))
        plt.specgram(self.amplitude,  Fs=self.fs, cmap = cmap)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.colorbar()
        return fig

    def initSpectrogram(self, imageItem, hist):
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        imageItem.scale(self.time[-1]/np.size(self.powerSpectrum, axis=1), math.pi/np.size(self.powerSpectrum, axis=0))
        self.setSpectrogramColor(hist, 0)

    def setSpectrogramColor(self, hist, slidervalue): # slidervalue -> 0: 4
        hist.gradient.restoreState({'mode': 'rgb','ticks': [(0.5, midColor[slidervalue]),(1.0, maxColor[slidervalue]),(0.0, minColor[slidervalue])]})
        hist.gradient.saveState()

    def plotSpectrogram(self, imageItem):
        self.powerSpectrum, self.freqenciesFound, _, _ = plt.specgram(self.amplitude, Fs=self.fs)
        # for more colormaps: https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html
        # Sxx contains the amplitude for each pixel
        imageItem.setImage(self.powerSpectrum)

    def moveSpectrogram(self, minIntensity, maxIntensity, plotItem, hist):
        # Fit the min and max levels of the histogram to the data available
        min = np.min(self.powerSpectrum)
        max = np.max(self.powerSpectrum)
        hist.setLevels(min + (max - min) * minIntensity, max * maxIntensity)
        # plotItem.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])

    def listen(self):
        winsound.PlaySound("output_sound" + str(self.winNumber) + ".wav", winsound.SND_ASYNC)
    def save(self):
        write("output_sound" + str(self.winNumber) + ".wav", self.fs, self.amplitude.astype(np.int16))
