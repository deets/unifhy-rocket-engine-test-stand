from pyqtgraph import PlotWidget,GraphicsLayoutWidget
from PyQt5 import QtWidgets, QtWidgets
import numpy as np
import pyqtgraph as pg
import bisect
from Model.streamManager import StreamManager
from scipy.signal import savgol_filter as sgf
import scipy.integrate as igt

class AnalyseViewModel:
    def __init__(self,analyseTabView,config):
        self.config = config
        self.tabView = analyseTabView
        self.setUpHandels()
        self.initControls()

    def setUpHandels(self):

        # get handels
        # combo boxes
        self.chnComboBox = self.tabView.findChild(QtWidgets.QComboBox,"chnNumComboBox")
        self.orientationComboBox = self.tabView.findChild(QtWidgets.QComboBox,"orientationComboBox")
        # buttons
        self.resetButton = self.tabView.findChild(QtWidgets.QPushButton,"resetButton")
        self.selectRoiButton = self.tabView.findChild(QtWidgets.QPushButton,"selectRoiButton")
        self.filterButton = self.tabView.findChild(QtWidgets.QPushButton,"filterButton")
        self.analyseButton = self.tabView.findChild(QtWidgets.QPushButton,"analyseButton")
        self.massCompButton = self.tabView.findChild(QtWidgets.QPushButton,"massCompButton")
        # labels
        self.preBurnLabel = self.tabView.findChild(QtWidgets.QLabel,"preBurnLabel")
        self.postBurnLabel = self.tabView.findChild(QtWidgets.QLabel,"postBurnLabel")
        self.startTimeLabel = self.tabView.findChild(QtWidgets.QLabel,"startTimeLabel")
        self.stopTimeLabel = self.tabView.findChild(QtWidgets.QLabel,"stopTimeLabel")
        self.idtLabel = self.tabView.findChild(QtWidgets.QLabel,"idtLabel")
        self.irtLabel = self.tabView.findChild(QtWidgets.QLabel,"irtLabel")
        self.atLabel = self.tabView.findChild(QtWidgets.QLabel,"atLabel")
        self.btLabel = self.tabView.findChild(QtWidgets.QLabel,"btLabel")
        self.maxThrustLabel = self.tabView.findChild(QtWidgets.QLabel,"maxThrustLabel")
        self.spImpulsLabel = self.tabView.findChild(QtWidgets.QLabel,"spImpulsLabel")
        self.totImpulsLabel = self.tabView.findChild(QtWidgets.QLabel,"totImpulsLabel")
        # line edits
        self.windowLineEdit = self.tabView.findChild(QtWidgets.QLineEdit,"windowLineEdit")
        self.orderLineEdit = self.tabView.findChild(QtWidgets.QLineEdit,"orderLineEdit")
        self.fuelMassLineEdit = self.tabView.findChild(QtWidgets.QLineEdit,"fuelMassLineEdit")
        # check boxes
        self.massCompCheckBox = self.tabView.findChild(QtWidgets.QCheckBox,"massCompCheckBox")
        self.calcMassCheckBox = self.tabView.findChild(QtWidgets.QCheckBox,"calcMassCheckBox")
        # graph view
        self.graphView = self.tabView.findChild(GraphicsLayoutWidget,"analyseGraphView")
        self.roi = None
        self.inf1 = None

    def initControls(self):
        self.chnComboBox.addItems(["Channel {}".format(num) for num in range(1,9,1)])
        self.orientationComboBox.addItems(["upwards","downwards","horizontal"])
        self.initGraph()
        self.selectRoiButton.state = "selectRoi"
        # connections
        self.resetButton.clicked.connect(self.resetGraphView)
        self.selectRoiButton.clicked.connect(self.selectRegions)
        self.analyseButton.clicked.connect(self.analyse)
        self.filterButton.clicked.connect(self.applyFilter)
        self.massCompButton.clicked.connect(self.computeMassCompensation)

    def resetGraphView(self):
        chnNum = self.chnComboBox.currentIndex()+1
        with StreamManager.numDataLock:
            if len(StreamManager.numData[chnNum])>=50:
                self.x = np.array(StreamManager.numData[0])
                self.y = np.array(StreamManager.numData[chnNum])

        scale = float(self.config.chnConfigs[chnNum-1].scale)
        offset = float(self.config.chnConfigs[chnNum-1].offset)
        self.y_ = self.y * scale + offset
        self.curve.setData(y=self.y_,x=self.x)
        if self.roi is None:
            self.roi = pg.LinearRegionItem([min(self.x),max(self.x)])
            self.Plt.addItem(self.roi)
        else:
            self.roi.setRegion([min(self.x),max(self.x)])
            self.roi.show()
        self.selectRoiButton.setText("Select Region of Interest")
        self.selectRoiButton.state = "selectRoi"
        self.selectRoiButton.show()
        if self.inf1 is not None:
            self.inf1.hide()
            self.inf2.hide()

    def initGraph(self):
        win: GraphicsLayoutWidget = self.graphView
        self.Plt = win.addPlot(title="",col=0,row=0)
        self.curve = self.Plt.plot(pen=(1,2*1.3))

    def selectRegions(self):
        if self.selectRoiButton.state == "selectRoi":
            self.cropDataToRegion()
            self.updateGraph()
            self.selectRoiButton.state = "selectPreBurnData"
            self.selectRoiButton.setText("Select Pre Burn Values")
        elif self.selectRoiButton.state == "selectPreBurnData":
            self.getPreBurnValues()
            self.selectRoiButton.state = "selectPostBurnData"
            self.selectRoiButton.setText("Select Post Burn Values")
        elif self.selectRoiButton.state == "selectPostBurnData":
            self.getPostBurnValues()
            self.calculateStartStopTime()

    def cropDataToRegion(self):
        x1, x2 = self.roi.getRegion()
        idx1 = max(bisect.bisect_left(self.x,x1),0)
        idx2 = min(bisect.bisect_right(self.x,x2),len(self.x)-1)
        self.x = self.x[idx1:idx2]
        self.y_ = self.y_[idx1:idx2]
        print(self.roi.getRegion())

    def getPreBurnValues(self):
        x1, x2 = self.roi.getRegion()
        idx1 = max(bisect.bisect_left(self.x,x1),0)
        idx2 = min(bisect.bisect_right(self.x,x2),len(self.x)-1)
        self.preBurnData = self.y_[idx1:idx2]
        self.preBurnValue = self.preBurnData.mean()
        self.preBurnStd = self.preBurnData.std()
        self.preBurnLabel.setText("{:.2f}".format(self.preBurnValue))

    def getPostBurnValues(self):
        x1, x2 = self.roi.getRegion()
        idx1 = max(bisect.bisect_left(self.x,x1),0)
        idx2 = min(bisect.bisect_right(self.x,x2),len(self.x)-1)
        self.postBurnData = self.y_[idx1:idx2]
        self.postBurnValue = self.postBurnData.mean()
        self.postBurnStd = self.postBurnData.std()
        self.postBurnLabel.setText("{:.2f}".format(self.postBurnValue))

    def calculateStartStopTime(self):
        # try to find the start value
        for i in range(len(self.x)):
            value = self.y_[i]
            if value > (max(self.preBurnData) + 2*self.preBurnStd):
                self.startTime = self.x[i]
                self.startTimeLabel.setText("{:.2f}".format(self.startTime))
                break

        # try to find the stop value
        for i in range(len(self.x)):
            value = self.y_[(i+1)*-1] # inverse the search direction
            if value > (max(self.postBurnData) + 2*self.postBurnStd):
                self.stopTime = self.x[(i+1)*-1]
                self.stopTimeLabel.setText("{:.2f}".format(self.stopTime))
                break
        if self.inf1 is None:
            self.inf1 = pg.InfiniteLine(angle=90, label='start time={:1.2f}'.format(self.startTime),
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50), 'movable': True})
            self.inf2 = pg.InfiniteLine(angle=90, label='stop time={:1.2f}'.format(self.stopTime),
                       labelOpts={'position':0.1, 'color': (200,200,100), 'fill': (200,200,200,50), 'movable': True})
            self.Plt.addItem(self.inf1)
            self.Plt.addItem(self.inf2)
            self.inf1.setPos([self.startTime,0])
            self.inf2.setPos([self.stopTime,0])
        else:
            self.inf1.setPos([self.startTime,0])
            self.inf2.setPos([self.stopTime,0])
            self.inf1.show()
            self.inf2.show()
        self.roi.hide()
        #self.curve.setData(fillLevel = min(self.y_))

    def updateGraph(self):
        self.curve.setData(x=self.x,y=self.y_)

    def analyse(self):
        # 1. get max thrust value
        self.maxThrust = max(self.y_)
        self.maxThrust_Newton = self.maxThrust * 9.81
        print("max thrust:{:0.2f}".format(self.maxThrust))
        # 2. get left 10% thrust time
        firstFound = False
        for i in range(len(self.x)):
            value = self.y_[i]
            if value > (self.maxThrust*0.1) and not firstFound:
                self.burnStartTime = self.x[i]
                print("burn time:{:0.2f}".format(self.burnStartTime))
                firstFound =True
            elif value > (self.maxThrust*0.75):
                self.riseTime = self.x[i]
                print("rise time:{:0.2f}".format(self.riseTime))
                break

        # 3. get right 10% thrust time
        firstFound = False
        for i in range(len(self.x)):
            value = self.y_[(i+1)*-1]
            if value > (self.maxThrust*0.1) and not firstFound:
                self.burnStopTime = self.x[(i+1)*-1]
                print("burn out time:{:0.2f}".format(self.burnStopTime))
                firstFound =True
            elif value > (self.maxThrust*0.75):
                self.fallTime = self.x[(i+1)*-1]
                print("fall time:{:0.2f}".format(self.fallTime))
                break

        # 4. get total impuls in Ns
        idx1 = max(bisect.bisect_left(self.x,self.startTime),0)
        idx2 = min(bisect.bisect_right(self.x,self.stopTime),len(self.x)-1)
        y_corr = (self.y_[idx1:idx2]-self.preBurnValue) * 9.81
        self.totImpuls = np.trapz(y= y_corr,x=self.x[idx1:idx2])
        print("Impuls:{:0.2f} Ns".format(self.totImpuls))
        # 5. get specific impuls
        m_tot = self.preBurnValue - self.postBurnValue
        self.spImpuls = self.totImpuls / (m_tot * 9.81)
        print("spezific Impuls:{:0.2f} s".format(self.spImpuls))
        # 6. update interface
        self.idtLabel.setText("{:0.2f} s".format(self.burnStartTime - self.startTime))
        self.irtLabel.setText("{:0.2f} s".format(self.riseTime - self.burnStartTime))
        self.btLabel.setText("{:0.2f} s".format(self.fallTime-self.burnStartTime))
        self.atLabel.setText("{:0.2f} s".format(self.burnStopTime-self.burnStartTime))
        self.maxThrustLabel.setText("{:0.2f} N".format(self.maxThrust_Newton))
        self.totImpulsLabel.setText("{:0.2f} Ns".format(self.totImpuls))
        self.spImpulsLabel.setText("{:0.2f} s".format(self.spImpuls))

    def applyFilter(self):
        try:
            windowSize = int(self.windowLineEdit.text())
            order = int(self.orderLineEdit.text())
            self.y_ = sgf(self.y_,windowSize,order,mode="nearest")
            self.updateGraph()
        except Exception as err:
            print("Ein Fehler ist aufgetreten!")
            print(err)

    def computeMassCompensation(self):
        # iterativly compute the mass flow and correct the sensor data
        # algorithm by David Madlener
        m_tot = self.preBurnValue - self.postBurnValue
        t0 = self.startTime
        t1 = self.stopTime
        idx0 = bisect.bisect_left(self.x,t0)
        idx1 = bisect.bisect_right(self.x,t1)
        S = self.y_[idx0:idx1] # get sensor data (kg)
        t = self.x[idx0:idx1]   # get time (s)
        P_old = 0
        m = np.ones(len(S)) * self.preBurnValue # initialize m(t) with constant pre burn values
        delta_P  = 1
        e = 0.00001

        while delta_P > e:
            F = S - m               # compute thrust F (kg)
            P_new = np.trapz(y=F,x=t) # integrate thrust (kg s)
            m_dot = -1 * F * (m_tot/P_new)
            m = igt.cumtrapz(m_dot,t,initial=m[0])
            delta_P = abs(P_new-P_old)
            P_old = P_new
            #print("delta_P:{}".format(delta_P))

        self.y_[:idx0] = self.y_[:idx0] - self.preBurnValue
        self.y_[idx0:idx1] = S - m      - self.preBurnValue
        self.y_[idx1:] = self.y_[idx1:] - self.postBurnValue
        self.updateGraph()
