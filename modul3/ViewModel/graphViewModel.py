from pyqtgraph import PlotWidget,GraphicsLayoutWidget
import numpy as np
import pyqtgraph as pg
from Model.streamManager import StreamManager
from scipy.signal import savgol_filter as sgf
from scipy.signal import decimate

class graphViewModel:
    def __init__(self,graphView,config,channelControlView):
        global plotW
        self.view: GraphicsLayoutWidget = graphView
        self.dataLines = []
        plotW = None
        self.channelControlView = channelControlView
        self.config = config
        self.drawPlots()

    def updateChannelSettings(self,chnNum,ctl,text):
        if (self.config.isStacked):
            self.updateStackedGraphView(chnNum,ctl,text)
        else:
            self.updateUnifiedGraphView(chnNum,ctl,text)

    def updateStackedGraphView(self,chnNum,ctl,text):
        if ctl=="title":
            item=self.view.getItem(chnNum-1,0)
            item.setTitle(text)

        if (ctl=="active"):
            if text=="2":
                self.view.getItem(chnNum-1,0).show()
                with StreamManager.numDataLock:
                    if len(StreamManager.numData[chnNum])>=1:
                        self.plotAxis[chnNum-1].setData(y=StreamManager.numData[chnNum],x=StreamManager.numData[0])
            elif text=="0":
                self.view.getItem(chnNum-1,0).hide()
                

    def updateUnifiedGraphView(self,chnNum,ctl,text):       
        if (ctl=="active"):
            if text=="2":
                try:
                    with StreamManager.numDataLock:
                        if len(StreamManager.numData[chnNum])>=1:
                            self.plotAxis[chnNum-1].setData(y=StreamManager.numData[chnNum],x=StreamManager.numData[0])
                            self.plotAxis[chnNum-1].show()
                except:
                    pass
            elif text=="0":
                self.plotAxis[chnNum-1].hide()

    def syncGraphViewWithConfig(self):
        pass

    def drawPlots(self):
        if self.config.isStacked:
            self.drawStackedPlots()
        else:
            self.drawUnifiedPlots()

    def drawStackedPlots(self):
        win: GraphicsLayoutWidget = self.view
        self.plotAxis  = []
        for i in range(1,9,1):
            if self.config.chnConfigs[i-1].active == "2":
                try:
                    with StreamManager.numDataLock:
                        plt=win.addPlot(title=self.config.chnConfigs[i-1].title, 
                                col=0,row=i-1)
                        self.plotAxis.append(plt.plot(x=np.array(StreamManager.numData[0]),
                                        y=np.array(StreamManager.numData[i]),pen=(i,8*1.3)))
                except:
                    pass
                plt.showGrid(x=True,y=True)
                print("plt type:",type(plt))
            else:
                plt=win.addPlot(title=self.config.chnConfigs[i-1].title ,col=0,row=i-1)
                self.plotAxis.append(plt.plot(pen=(i,8*1.3)))
                plt.showGrid(x=True,y=True)
                plt.hide()
        for i in range(0,7,1):
            print("item type:",type(self.view.getItem(i,0)))
            self.view.getItem(i,0).setXLink(self.view.getItem(i+1,0))

    def drawUnifiedPlots(self):
        win: GraphicsLayoutWidget = self.view
        self.unifiedPlt = win.addPlot(title="",col=0,row=0)
        
        #self.unifiedPlt.addLegend()
        self.plotAxis = []
        if len(StreamManager.numData[0])>5:
            x_1 = np.array(StreamManager.numData[0])
            x_2 = x_1[1:]
            d_x = x_2 - x_1[0:-1]
            print("sigma of time:",d_x.std())
            print("mean of time:",d_x.mean())
        with StreamManager.numDataLock:
            for i in range(1,9,1):
                if self.config.chnConfigs[i-1].active == "2":
                    scale = float(self.config.chnConfigs[i-1].scale)
                    offset = float(self.config.chnConfigs[i-1].offset)
                    y_c = np.array(StreamManager.numData[i]) * scale + offset
                    self.plotAxis.append(self.unifiedPlt.plot(x=np.array(StreamManager.numData[0]),
                                        y=y_c,pen=(i,8*1.3),
                                        name=self.config.chnConfigs[i-1].title.format(i)))
                    print("unified plt item:",type(self.plotAxis[-1]))   
                else:
                    self.plotAxis.append(self.unifiedPlt.plot(pen=(i,8*1.3),
                                        name=self.config.chnConfigs[i-1].title.format(i)))
    
        
    def update(self):  
        if self.config.isStacked:
            for chnNum in range(1,9,1):
                try:
                    with StreamManager.numDataLock:
                        if len(StreamManager.numData[chnNum])>=1:
                            self.plotAxis[chnNum-1].setData(y=np.array(StreamManager.numData[chnNum]),x=np.array(StreamManager.numData[0]))
                except:
                    pass
        else:
            for chnNum in range(1,9,1):
                if self.config.chnConfigs[chnNum-1].active == "2":
                    with StreamManager.numDataLock:
                        if len(StreamManager.numData[chnNum])>=50:
                            scale = float(self.config.chnConfigs[chnNum-1].scale)
                            offset = float(self.config.chnConfigs[chnNum-1].offset)
                            y_c = np.array(StreamManager.numData[chnNum]) * scale + offset
                            #y_f = sgf(y_c,21,3,mode="nearest")
                            y_f = y_c
                            x_f = np.array(StreamManager.numData[0])
                            #y_f = decimate(y_c,50)
                            
                            self.plotAxis[chnNum-1].setData(y=y_f,x=x_f)
                  

    def clearGraphView(self):
        win: GraphicsLayoutWidget = self.view
        win.clear()


    def applyConfig(self):
        pass