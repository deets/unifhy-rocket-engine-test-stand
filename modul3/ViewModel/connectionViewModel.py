import serial, time
import serial.tools.list_ports as lp
from PyQt5 import QtGui, QtWidgets

class ConnectionViewModel:
    def __init__(self,connectionView):
        # view references
        self.view = connectionView
        self.serialButton = self.view.findChild(QtGui.QPushButton,"serialButton")
        self.serialComboBox = self.view.findChild(QtGui.QComboBox,"serialComboBox")
        self.filePathLineEdit = self.view.findChild(QtGui.QLineEdit,"filePathLineEdit")
        self.filePathButton = self.view.findChild(QtGui.QPushButton,"filePathButton")

        #connection
        self.serialButton.clicked.connect(self.scanSerialPorts)
        self.filePathButton.clicked.connect(self.browseFile)

    def scanSerialPorts(self):
        portObjects = lp.comports()
        portNames = [port.device for port in portObjects]
        self.serialComboBox.clear()
        self.serialComboBox.addItems(portNames)

    def browseFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self.view,caption="Choose Data File")
        self.filePathLineEdit.setText(path[0])
        