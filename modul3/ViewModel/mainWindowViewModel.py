from PyQt5 import QtWidgets, QtCore, uic, QtGui
from pyqtgraph import PlotWidget,GraphicsLayoutWidget
from View.channelControlView import channelControlView
from ViewModel.graphViewModel import graphViewModel
from ViewModel.appConfig import appConfig
from Model.streamManager import StreamManager
from Model.streamManager import StreamParser
from ViewModel.connectionViewModel import ConnectionViewModel
from ViewModel.calibGraphViewModel import CalibGraphViewModel
from ViewModel.analyseViewModel import AnalyseViewModel
import pyqtgraph as pg
import numpy as np
import bisect

class MainWindowViewModel(QtWidgets.QMainWindow):
    # custom signals
    mySignal = QtCore.pyqtSignal()
    myBoolSignal = QtCore.pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(MainWindowViewModel, self).__init__(*args, **kwargs)
        self.config = appConfig() 
        #Load the UI Page
        uic.loadUi('./View/mainWindow.ui', self)
        self.initChannelControlView(self.config.chnConfigs)
        self.initGraphView(self.graphView) # pass the handel to the graphViewModel
        self.initControls()
        self.initStreamManager()
        self.initConnectionViewModel()
        self.initCalibGraphViewModel()
        self.initAnalysisViewModel()
        # connections
        #self.channelControlView.channelSettingChanged.connect(self.graphViewModel.updateChannelSettings)
        self.channelControlView.channelSettingChanged.connect(self.changeConfig)
        self.saveConfigButton.clicked.connect(self.saveConfig)
        self.startStopStreamButton.toggled.connect(self.startStopStream)
        self.streamManager.dataUpdated.connect(self.updateGraphData)
        self.calibGraphViewModel.newCalibValues.connect(self.updateChannelCalib)
        self.resetStreamButton.clicked.connect(self.resetStream)
        self.menuExportRawData.triggered.connect(self.exportRawData)

    def initCalibGraphViewModel(self):
        self.calibGraphViewModel = CalibGraphViewModel(self.calibGraphView,self.calibControlFrame)

    def initConnectionViewModel(self):
        self.connectionViewModel = ConnectionViewModel(self.connectionTab)

    def initChannelControlView(self,config):
        self.channelControlView = channelControlView(config)
        self.scrollArea.setWidget(self.channelControlView)

    def initGraphView(self,graphView):
        self.graphViewModel = graphViewModel(graphView,self.config,self.channelControlView)
    
    def initControls(self):
        conf = self.config
        self.stackedGraphRadioButton.setChecked(conf.isStacked)
        self.stackedGraphRadioButton.toggled.connect(self.plotLayoutChanged)
        self.unifiedGraphRadioButton.setChecked(not conf.isStacked)
        self.multiAxisCheckBox.setChecked(conf.isMultiAxis)

    def initAnalysisViewModel(self):
        #self.tabWidget.setTabEnabled(3,False)
        self.analysisViewModel = AnalyseViewModel(self.tabWidget,self.config)
    def initStreamManager(self):
        self.streamManager = StreamManager()

    def startStopStream(self,enable):
        print(len(self.streamManager.numData[0]))
        if enable:
            self.startStopStreamButton.setText("Stop Stream")
            self.streamManager.startStream(self.getStreamConfig())
            self.tabWidget.setTabEnabled(3,False)
            self.resetStreamButton.setEnabled(False)
        else:
            self.startStopStreamButton.setText("Start Stream")
            self.streamManager.stopStream()
            self.tabWidget.setTabEnabled(3,True)
            self.resetStreamButton.setEnabled(True)

    def getStreamConfig(self):
        if self.fileStreamRadioButton.isChecked():
            config = {"streamType":"FileStream","filePath":self.connectionViewModel.filePathLineEdit.text()}
            return config
        elif self.serialStreamRadioButton.isChecked():
            config = {"streamType":"SerialStream","serialPort":self.serialComboBox.currentText()}
            return config

    def saveConfig(self):
        self.config.saveConfig()
        self.saveConfigButton.setEnabled(False)

    def changeConfig(self,chnNum,ctl,text):
        self.graphViewModel.updateChannelSettings(chnNum,ctl,text)
        self.config.changeConfig(chnNum,ctl,text)
        self.saveConfigButton.setEnabled(True)

    def plotLayoutChanged(self,isStacked):
        self.config.changeGraphLayout(isStacked)
        self.graphViewModel.clearGraphView()
        
        if isStacked:
            self.graphViewModel.drawStackedPlots()
        else:
            self.graphViewModel.drawUnifiedPlots()

    def updateGraphData(self):
        self.graphViewModel.update()

    def updateChannelCalib(self,chnNum,scale,offset):
        self.channelControlView.updateCalibration(chnNum,scale,offset)

    def resetStream(self):
        StreamManager.rawData = bytearray()
        StreamManager.numData = [[],[],[],[],[],[],[],[],[]]
        StreamParser.seeker_position = 0
        StreamParser.rawPackage = bytearray()
        self.updateGraphData()

    def exportRawData(self):
        path = QtGui.QFileDialog.getSaveFileName(self, 'data.raw')
        print(path[0])
        if not (path==''):
            with open(path[0],'wb') as file:
                with StreamManager.dataLock:
                    file.write(StreamManager.rawData)

    def importCSVfile(self):
        pass
        

    """ def plot(self, hour, temperature):
        self.graphWidget.plot(hour, temperature)
        vb = self.graphWidget.getViewBox()
        #vb.setMouseMode(pg.ViewBox.RectMode)
        # only zoom on x axis
        self.graphWidget.setMouseEnabled(y=False)                                                          
        # auto update y axis to visible min max values
        self.graphWidget.sigRangeChanged.connect(self.update_y_axis)  """
        
        
        

    # custom slots
    """ def pushButton_clicked(self):
        print("Click!")
        self.myBoolSignal.emit(False)
    
    def mySignalEmitted(self):
        print("Emitted!")

    def inf1_restrict_position(self):
        idx = min(bisect.bisect_left(self.data[0],self.inf1.getXPos()),len(self.data[0])-1)
        self.inf1.setPos([self.data[0][idx],0])
        self.inf1.label.setFormat('y={:0.2f}'.format(self.data[1][idx])) """

    """ def update_y_axis(self): """
        # fancy code to update y axis to min max values when only x zooming is enabled
    """ self.graphWidget.sigRangeChanged.disconnect(self.update_y_axis) 
        vb = self.graphWidget.getViewBox()
        xRange = vb.viewRange()[0]
        print(xRange)
        idyL = min(bisect.bisect_left(self.data[0],xRange[0]),len(self.data[0])-1)
        idyH = min(bisect.bisect_left(self.data[0],xRange[1]),len(self.data[0])-1)
        print(self.data[1][idyL],self.data[1][idyH])
        print(min(self.data[1][idyL:idyH]))
        vb.setYRange(min(self.data[1][idyL:idyH]),max(self.data[1][idyL:idyH]))
        self.graphWidget.sigRangeChanged.connect(self.update_y_axis)  """