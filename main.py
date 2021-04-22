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
import numpy as np
import matplotlib.pyplot as plt
import scipy 
from classes import signal
from scipy.io import wavfile
import pathlib
from processfunc import processFrequencyBand

cmaps = ['plasma', 'Greys', 'viridis', 'magma', 'inferno']


# class definition for application window components like the ui
class ApplicationWindow(QtWidgets.QMainWindow):
    windowsNumber = 0
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.__class__.windowsNumber = self.__class__.windowsNumber + 1
        # print("---------BEFORE SETTING WINDOW GUI-----------")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cmap = cmaps[0]
        for cmap in cmaps:
            self.ui.pallet.addItem(cmap)
        self.ui.pallet.activated[str].connect(self.setSpectrogramColor)
        self.inputSignal = False
        self.outputSignal = False
        signal.timer.start()
        self.ui.open.triggered.connect(self.open)
        self.ui.save.triggered.connect(self.saveAs)
        self.ui.zoomIn.clicked.connect(self.zoomIn)
        self.ui.zoomOut.clicked.connect(self.zoomOut)
        # signal.timer.timeout.connect(self.moveSignals)
        self.slidervalues = np.ones((10,), dtype =float)
        for slider in self.ui.sliders:
            slider.sliderReleased.connect(self.equalizeSignal)
        self.ui.max_slider.sliderReleased.connect(self.adjustSpectrogram)
        self.ui.min_slider.sliderReleased.connect(self.adjustSpectrogram)
        self.ui.scroll.sliderReleased.connect(self.scrollView)

    def __del__(self):
        self.__class__.windowsNumber = self.__class__.windowsNumber - 1

    def zoomOut(self):
        if self.inputSignal and self.outputSignal:
            self.inputSignal.zoomOut()
            self.outputSignal.zoomOut()
            self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def zoomIn(self):
        if self.inputSignal and self.outputSignal:
            self.inputSignal.zoomIn()
            self.outputSignal.zoomIn()
            self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def scrollView(self):
        slidervalue = self.ui.scroll.value()
        self.inputSignal.scrollSignal(slidervalue)
        self.outputSignal.scrollSignal(slidervalue)
        self.outputSignal.plotSpectrogram(self.ui.output_spectrogram)
        self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def equalizeSignal(self):
        if self.inputSignal and self.outputSignal:
            idx = 0
            for slider in self.ui.sliders:
                self.slidervalues[idx] = slider.value()/ 20
                idx = idx + 1
            self.outputSignal.updateSignal(processFrequencyBand(self.inputSignal.amplitude, self.inputSignal.fs,self.slidervalues))
            self.outputSignal.plotSpectrogram(self.ui.output_spectrogram)
            self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def adjustSpectrogram(self):
        if self.inputSignal and self.outputSignal:
                self.max_intensity = (self.ui.max_slider.value()/1000)
                self.min_intensity = (self.ui.min_slider.value()/1000)
                self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def open(self):
        if self.inputSignal:
            # print("----------CALL CHILD-----------")
            child_window()
        else:
            files_name = QtGui.QFileDialog.getOpenFileName( self, 'Open only wav', os.getenv('HOME') ,"wav(*.wav)" )
            path = files_name[0]

            if pathlib.Path(path).suffix == ".wav":
                samplerate, data = wavfile.read(path)
                self.inputSignal = signal(data, samplerate, self.ui.input_signal, self.__class__.windowsNumber)
                self.outputSignal = signal(data, samplerate, self.ui.output_signal, self.__class__.windowsNumber)   
                self.max_intensity = (self.ui.max_slider.value()/1000)
                self.min_intensity = (self.ui.min_slider.value()/1000)
                self.outputSignal.plotSpectrogram(self.ui.output_spectrogram)
                self.outputSignal.initSpectrogram(self.ui.output_spectrogram, self.ui.hist)
                self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def moveSignals(self):
        if self.inputSignal:
            self.inputSignal.moveGraph()
            self.outputSignal.moveGraph()
            self.outputSignal.plotSpectrogram(self.ui.output_spectrogram)
            self.outputSignal.moveSpectrogram(self.min_intensity, self.max_intensity, self.ui.SpectrogramPlotItem, self.ui.hist)

    def saveAs(self):
        if self.inputSignal and self.outputSignal:
            report = PdfPages('report' + str(self.__class__.windowsNumber) + '.pdf')
            report.savefig(self.inputSignal.getFigure())
            report.savefig(self.outputSignal.getFigure())
            report.savefig(self.inputSignal.getSpectrogram(self.cmap))
            report.savefig(self.outputSignal.getSpectrogram(self.cmap))
            report.close()

    def setSpectrogramColor(self, text):
        for idx in range(len(cmaps)):
            if cmaps[idx] == text:
                self.outputSignal.setSpectrogramColor(self.ui.hist ,idx)
        self.cmap = text

# function for launching a QApplication and running the ui and main window
def window():
    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    sys.exit(app.exec_())

def child_window():
    global win
    win = ApplicationWindow()
    win.show()

if __name__ == "__main__":
    window()