from pyqtgraph import PlotWidget,GraphicsLayoutWidget
import numpy as np
import pyqtgraph as pg
from Model.streamManager import StreamManager
from PyQt5 import QtCore, QtGui, QtWidgets

class CalibGraphViewModel(QtCore.QObject):
    # signals
    newCalibValues = QtCore.pyqtSignal([int,str,str])

    def __init__(self,calibGraphView,calibControlls=None):
        super().__init__()
        self.view: GraphicsLayoutWidget = calibGraphView
        self.controlls = calibControlls
        self.setUpControlHandels()
        self.initGraph()
        self.graphTimer = QtCore.QTimer()
        self.graphTimer.timeout.connect(self.updateGraph)
        self.graphTimer.start(1000)

    def setUpControlHandels(self):
        # get handels
        self.comboBox = self.controlls.findChild(QtWidgets.QComboBox,"channelComboBox")
        self.referenceValue = self.controlls.findChild(QtWidgets.QLineEdit,"referenceLineEdit")
        self.addValueButton = self.controlls.findChild(QtWidgets.QPushButton,"addValueButton")
        self.clearButton = self.controlls.findChild(QtWidgets.QPushButton,"clearButton")
        self.applyButton = self.controlls.findChild(QtWidgets.QPushButton,"applyButton")
        self.table = self.controlls.findChild(QtWidgets.QTableWidget,"tableWidget")
        self.scaleText = self.controlls.findChild(QtWidgets.QLabel,"scaleOutLabel")
        self.offsetText = self.controlls.findChild(QtWidgets.QLabel,"offsetOutLabel")
        self.rawSigmaText = self.controlls.findChild(QtWidgets.QLabel,"rawSigmaOutLabel")
        self.scaledSigmaText = self.controlls.findChild(QtWidgets.QLabel,"scaledSigmaOutLabel")

        # set up comboBox
        self.comboBox.addItems(["Channel {}".format(num) for num in range(1,9,1)])

        #set up tabel widget
        self.table.setHorizontalHeaderLabels(["µ","𝞂","ref"])

        # connections
        self.addValueButton.clicked.connect(self.addCalibrationValue)
        self.applyButton.clicked.connect(self.applyCalibValues)
        self.clearButton.clicked.connect(self.clearCalibValues)

    def initGraph(self):
        win: GraphicsLayoutWidget = self.view
        self.Plt = win.addPlot(title="",col=0,row=0)
        self.histPlot = self.Plt.plot(pen=(1,2*1.3),stepMode=True)
        self.normalDist = self.Plt.plot(pen=(2,2*1.3))
        self.mu = None
        self.samples = [[],[],[]]

    def addCalibrationValue(self):
        try:
            refValue = float(self.referenceValue.text())
        except:
            refValue = 0

        if (self.mu is not None):
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            self.table.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem("{}".format(self.mu)))
            self.table.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem("{}".format(self.s)))
            self.table.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem("{}".format(refValue)))
            self.samples[0].append(self.mu)
            self.samples[1].append(refValue)
            self.samples[2].append(self.s)
            # calculate coefficians of linear polynom y = p1*x+p0, see numpy doc for more
            if len(self.samples[0])>2:
                p = np.polyfit(x=np.array(self.samples[0]),y=np.array(self.samples[1]),deg=1,
                                        w=1/np.array(self.samples[2]))
                print(p)
                meanSigma = np.array(self.samples[2]).mean()
                self.scaleText.setText("{:.3e}".format(p[0]))
                self.offsetText.setText("{:.3e}".format(p[1]))
                self.rawSigmaText.setText("±{:.3e}".format(meanSigma*3))
                self.scaledSigmaText.setText("±{:.3e}".format(meanSigma*p[0]*3))

    def clearCalibValues(self):
        self.samples = [[],[],[]]
        self.table.clearContents()

    def applyCalibValues(self):
        if len(self.samples[0])>2:
            self.newCalibValues.emit(self.comboBox.currentIndex()+1,self.scaleText.text(),self.offsetText.text())

    def updateGraph(self):
        nSamples = 1000
        nBins = 40
        chnNum = self.comboBox.currentIndex()+1
        with StreamManager.numDataLock:
            if len(StreamManager.numData[chnNum])>nSamples:
                # get the latest 500 data points
                y_data=np.array(StreamManager.numData[chnNum][-nSamples:])
                mu = y_data.mean() # get mean
                s = y_data.std()    # get standard deveation
                self.mu = mu
                self.s = s
                self.Plt.setTitle("Mittelwert µ:{:.3e}, Standardabweichung 𝞂:{:.3e}".format(mu,s))
                # compute 40 histogram bins in a 6 sigma interval
                y_h, x_h = np.histogram(y_data,bins=np.linspace(mu-3*s,mu+3*s,nBins))
                # normalize the histogramm
                y_h = y_h / nSamples / (6*s/nBins)
                # compute normal dist for comparison
                y_nd = 1/(2*s**2*np.pi)**0.5 * np.e**(-(x_h-mu)**2/(2*s**2))
                self.histPlot.setData(x_h,y_h)
                self.normalDist.setData(x_h,y_nd)

                #print("unified plt item:",type(self.plotAxis[-1]))
