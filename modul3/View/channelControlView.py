from PyQt5 import QtWidgets, uic, QtCore,QtGui
import pyqtgraph as pg
class channelControl(QtWidgets.QFrame):
    # custom signals
    channelSettingChanged = QtCore.pyqtSignal([int,str,str])

    def __init__(self, channelNum, title, unit, offset, scale, active):
        super(channelControl, self).__init__()
        self.channelColors = []
        self.createChannelColors() 
        self.titleLine = QtWidgets.QLineEdit(title)
        self.titleLine.textChanged.connect(self.titleChanged)
        self.unitLine = QtWidgets.QLineEdit(unit)
        self.unitLine.textChanged.connect(self.unitChanged)
        self.offsetLine = QtWidgets.QLineEdit(offset)
        self.offsetLine.textChanged.connect(self.offsetChanged)
        self.scaleLine = QtWidgets.QLineEdit(scale)
        self.scaleLine.textChanged.connect(self.scaleChanged)
        self.activeCheckBox=QtWidgets.QCheckBox()
        self.activeCheckBox.setChecked(active=="2")
        self.activeCheckBox.stateChanged.connect(self.isActiveChanged)

        self.channelNum = channelNum
        channelColor = self.channelColors[channelNum-1].color()
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.WindowText,channelColor)
        layout = QtWidgets.QFormLayout()
        label = QtWidgets.QLabel()
        label.setPalette(pal)
        label.setText("Channel {0}".format(channelNum))
        layout.addRow(label)
        layout.addRow(QtWidgets.QLabel("title"),self.titleLine)
        layout.addRow(QtWidgets.QLabel("Unit"),self.unitLine)
        layout.addRow(QtWidgets.QLabel("Offset"),self.offsetLine)
        layout.addRow(QtWidgets.QLabel("Scale"),self.scaleLine)
        layout.addRow(QtWidgets.QLabel("Channel active"),self.activeCheckBox)
        self.setLayout(layout)
        self.setMinimumSize(0,200)
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

    def titleChanged(self,text):
        self.channelSettingChanged.emit(self.channelNum,"title",text)
    
    def unitChanged(self,text):
        self.channelSettingChanged.emit(self.channelNum,"unit",text)

    def offsetChanged(self,text):
        self.channelSettingChanged.emit(self.channelNum,"offset",text)

    def scaleChanged(self,text):
        self.channelSettingChanged.emit(self.channelNum,"scale",text)

    def isActiveChanged(self,state):
        self.channelSettingChanged.emit(self.channelNum,"active","{}".format(state))

    def createChannelColors(self):
        for i in range(1,9,1):
            self.channelColors.append(pg.mkPen(i,8*1.3))    

class channelControlView(QtWidgets.QWidget):
    channelSettingChanged = QtCore.pyqtSignal([int,str,str])
    

    def __init__(self,configs):
        super(channelControlView, self).__init__()
        self.configs = configs

        layout = QtWidgets.QVBoxLayout()
        for i in range(1,9,1):
            # create channelControlWidget and add it to the view
            layout.addWidget(channelControl(i,configs[i-1].title,configs[i-1].unit,configs[i-1].offset,configs[i-1].scale,configs[i-1].active))
            # make sure changed settings are propagated upwards
            layout.itemAt(i-1).widget().channelSettingChanged.connect(self.channelControlViewChanged)
        
        self.setLayout(layout)

    def channelControlViewChanged(self,channelNum,ctl,text):
        self.channelSettingChanged.emit(channelNum,ctl,text)
        print(channelNum,ctl,text)

    def updateCalibration(self,chnNum,scale,offset):
        chnControl: channelControl = self.layout().itemAt(chnNum-1).widget()
        chnControl.scaleLine.setText(scale)
        chnControl.offsetLine.setText(offset)
        
        print(self.layout().itemAt(chnNum-1).widget())
        print("Num:",chnNum,"scale:",scale,"offset:",offset)


