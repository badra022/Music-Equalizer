###########################################################
# authors: Ahmed Badra,
#          Hassan Hosni,
#          Yousof Elhely,
#          Moamen Gamal
#
# title: Biosignal viewer
#
# file: main program file (RUN THIS FILE)
############################################################

# libraries needed for main python file
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from gui import Ui_MainWindow
import os
from matplotlib.backends.backend_pdf import PdfPages
from librosa import display
import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy 
from IPython.display import Audio
from scipy.io.wavfile import write
from scipy.io import wavfile
from classes import signal
import pathlib
from processfunc import processFrequencyBand

MAX_SLIDER_IDX = 10
MIN_SLIDER_IDX = 11


# class definition for application window components like the ui
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pallet.addItem("plasma")
        self.ui.pallet.addItem("Greys")
        self.ui.pallet.addItem("viridis")
        self.ui.pallet.addItem("magma")
        self.ui.pallet.addItem("inferno")
        self.ui.pallet.activated[str].connect(self.changepallet)  
        self.inputSignal = False
        self.outputSignal = False
        signal.timer.start()
        self.ui.open.triggered.connect(self.open)
        self.ui.save.triggered.connect(self.saveAs)
        self.ui.zoomIn.clicked.connect(self.zoomIn)
        self.ui.zoomOut.clicked.connect(self.zoomOut)
        # signal.timer.timeout.connect(self.moveSignals)
        self.slidervalues = np.ones((10,), dtype =float)
        self.ui.sliders[0].sliderReleased.connect(lambda: self.process(0))
        self.ui.sliders[1].sliderReleased.connect(lambda: self.process(1))
        self.ui.sliders[2].sliderReleased.connect(lambda: self.process(2))
        self.ui.sliders[3].sliderReleased.connect(lambda: self.process(3))
        self.ui.sliders[4].sliderReleased.connect(lambda: self.process(4))
        self.ui.sliders[5].sliderReleased.connect(lambda: self.process(5))
        self.ui.sliders[6].sliderReleased.connect(lambda: self.process(6))
        self.ui.sliders[7].sliderReleased.connect(lambda: self.process(7))
        self.ui.sliders[8].sliderReleased.connect(lambda: self.process(8))
        self.ui.sliders[9].sliderReleased.connect(lambda: self.process(9))
        self.ui.max_slider.sliderReleased.connect(lambda: self.process(MAX_SLIDER_IDX))
        self.ui.min_slider.sliderReleased.connect(lambda: self.process(MIN_SLIDER_IDX))
        self.ui.scroll.sliderReleased.connect(self.scrollView)
        self.cmap = 'plasma'

    def zoomOut(self):
        self.inputSignal.zoomOut()
        self.outputSignal.zoomOut()
        self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
            maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)

    def zoomIn(self):
        self.inputSignal.zoomIn()
        self.outputSignal.zoomIn()
        self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
            maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)

    def scrollView(self):
        slidervalue = self.ui.scroll.value()
        self.inputSignal.scrollSignal(slidervalue)
        self.outputSignal.scrollSignal(slidervalue)
        self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
            maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)

    def process(self, idx):
        if self.inputSignal and self.outputSignal:
            if idx == MAX_SLIDER_IDX:
                self.max_freq = (self.ui.max_slider.value()/100) * (self.outputSignal.fs / 2)
                self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
                 maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)
            elif idx == MIN_SLIDER_IDX:
                self.min_freq = (self.ui.min_slider.value()/100) * (self.outputSignal.fs / 2)
                print("min frequency: ", self.min_freq)
                self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
                 maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)
            else:
                factor = self.ui.sliders[idx].value() / 20
                self.slidervalues[idx] = factor
                print("factor ", factor, "On slider ",idx)
                del self.outputSignal
                self.outputSignal = signal(processFrequencyBand(self.inputSignal.amplitude, self.inputSignal.fs,self.slidervalues), self.inputSignal.fs, self.ui.output_signal)
                self.outputSignal.plotSpectrogram(cmap = "plasma", minfreq = self.min_freq ,
                 maxfreq = self.max_freq, imageItem = self.ui.output_spectrogram, hist = self.ui.hist)

    def open(self):
        if self.inputSignal:
            child_window()
        else:
            files_name = QtGui.QFileDialog.getOpenFileName( self, 'Open only wav', os.getenv('HOME') ,"wav(*.wav)" )
            path = files_name[0]

            if pathlib.Path(path).suffix == ".wav":
                samplerate, data = wavfile.read(path)
                self.inputSignal = signal(data, samplerate, self.ui.input_signal)
                self.outputSignal = signal(data, samplerate, self.ui.output_signal)
                self.max_freq = (self.ui.max_slider.value()/100) * (self.outputSignal.fs / 2)
                self.min_freq = (self.ui.min_slider.value()/100) * (self.outputSignal.fs / 2)
                self.changepallet("plasma")

                powerSpectrum, time, frequencies = self.outputSignal.plotSpectrogram('plasma', self.min_freq, self.max_freq, self.ui.output_spectrogram, self.ui.hist)
                # Scale the X and Y Axis to time and frequency (standard is pixels)
                self.ui.output_spectrogram.scale(time[-1]/np.size(powerSpectrum, axis=1),
                frequencies[-1]/np.size(powerSpectrum, axis=0))

    def moveSignals(self):
        if self.inputSignal:
            self.inputSignal.moveGraph()
        if self.outputSignal:
            self.outputSignal.moveGraph()

    def saveAs(self):
        if self.inputSignal and self.outputSignal:
            report = PdfPages('report.pdf')
            report.savefig(self.inputSignal.getFigure())
            report.savefig(self.outputSignal.getFigure())
            report.savefig(self.inputSignal.getSpectrogram(self.min_freq, self.max_freq, self.cmap))
            report.savefig(self.outputSignal.getSpectrogram(self.min_freq, self.max_freq, self.cmap))
            report.close()

    def changepallet(self, text):
        if text == "plasma": #plasma
            self.ui.hist.gradient.restoreState(
                {'mode': 'rgb',
                'ticks': [(0.5, (0, 182, 188, 255)),
                        (1.0, (246, 111, 0, 255)),
                        (0.0, (75, 0, 113, 255))]})
            self.ui.hist.gradient.saveState()
            self.cmap = 'plasma'
        elif text == "Greys": #Greys
            self.ui.hist.gradient.restoreState(
                    {'mode': 'rgb',
                    'ticks': [(0.5, (128, 128, 128, 255)),
                            (1.0, (0, 0, 0, 255)),
                            (0.0, (255, 255, 255, 255))]})
            self.ui.hist.gradient.saveState()
            self.cmap = 'Greys'
        elif text == "viridis": #viridis
            self.ui.hist.gradient.restoreState(
                    {'mode': 'rgb',
                    'ticks': [(0.5, (0, 128, 128, 255)),
                            (0.0, (102, 0, 34, 255)),
                            (1.0, (230, 230, 0, 255))]})
            self.ui.hist.gradient.saveState()
            self.cmap = 'viridis'
        elif text == "magma": #magma
            self.ui.hist.gradient.restoreState(
                    {'mode': 'rgb',
                    'ticks': [(0.5, (230,0,115, 255)),
                            (1.0, (0,0,0, 255)),
                            (0.0, (255,255,255, 255))]})
            self.ui.hist.gradient.saveState()
            self.cmap = 'magma'
        elif text == "inferno": #inferno
            self.ui.hist.gradient.restoreState(
                    {'mode': 'rgb',
                    'ticks': [(0.5, (204, 0, 0, 255)),
                            (1.0, (0, 0, 0, 255)),
                            (0.0, (255,255,255, 255))]})
            self.ui.hist.gradient.saveState()
            self.cmap = 'inferno'

# function for launching a QApplication and running the ui and main window
def window():
    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    sys.exit(app.exec_())

def child_window():
    win = ApplicationWindow()
    win.show()

if __name__ == "__main__":
    window()