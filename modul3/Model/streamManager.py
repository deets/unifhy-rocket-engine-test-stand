import threading
from serial import Serial
import serial
from time import sleep
from PyQt5 import QtCore

class StreamManager(QtCore.QObject):
    # global data, should be thread safe
    dataLock = threading.Lock()
    rawData = bytearray()
    # global available numerical data listing: [time[],chn1[],chn2[],...,chn8[]]
    numDataLock = threading.Lock()
    numData = [[],[],[],[],[],[],[],[],[]]
    # signals
    dataUpdated = QtCore.pyqtSignal()

    def __init__(self):
        super(StreamManager, self).__init__()
        self.parser = StreamParser()

    def startStream(self,config):
        # start stream thread
        self.streamThread = StreamThread(config)
        StreamThread.stop_thread = False
        self.streamThread.start()

        # start clocked parser
        self.streamTimer = QtCore.QTimer(self)
        self.streamTimer.timeout.connect(self.streamDataUpdated)
        self.streamTimer.start(10) # 10ms 

    def stopStream(self):
        StreamThread.stop_thread = True
        self.streamThread.join()

    def streamDataUpdated(self):
        self.parser.parseStreamData()
        self.dataUpdated.emit()


class StreamThread(threading.Thread):
    stop_thread = True
    stream_rest = 0.01 # default 100ms

    def __init__(self,config):
        super().__init__()
        self.streamType = None
        self.serialPort = None
        self.filePath = None

        for attribute,value in config.items():
            self.__setattr__(attribute,value)

    def run(self):       
        if self.streamType == "FileStream":
            self.startFileStream()

        elif self.streamType == "SerialStream":
            self.startSerialStream()

        elif self.streamType == "HTTPStream":
            pass
 
        return

    def startFileStream(self):
        with open(self.filePath,"rb") as f:
            print("Reading from: {}".format(self.filePath))
            fileType = self.filePath.split('.')[1]
            if fileType == "csv":
                lines = f.readlines()
                for line in lines:
                    d_line = line.decode('ascii')
                    words = d_line.split()
                    if (len(words) == 2):
                        if (words[0]!='#'):
                            with StreamManager.numDataLock:            
                                StreamManager.numData[0].append(float(words[0]))
                                StreamManager.numData[1].append(float(words[1]))
            else:
                with StreamManager.dataLock:
                    StreamManager.rawData.extend(f.read())
            #StreamThread.stop_thread = True


    def startSerialStream(self):
        streamSerialSetup = {"baudrate":38400,"parity":getattr(serial,"PARITY_NONE"),
                            "bytesize":getattr(serial,"EIGHTBITS"),
                            "stopbits":getattr(serial,"STOPBITS_ONE"),"port":self.serialPort}

        with Serial(**streamSerialSetup) as ser:
            print("created serial stream")
            while(not StreamThread.stop_thread):    
                temp_data = ser.read()
                if len(temp_data) > 0:
                    #print(temp_data)
                    with StreamManager.dataLock:
                        StreamManager.rawData.extend(temp_data)
                        #print(temp_data)
                # rest the thread to free resources
                #sleep(StreamThread.stream_rest) 

    def startHTTPStream(self):
        pass

class StreamParser():
    seeker_position = 0
    rawPackage = bytearray()
    def __init__(self):
        pass

    def parseStreamData(self):
        channelValues = [[],[]]    # a list containing the parsed numerical channel values
        time = [] # parsed time stamps
        # get lock on rawData and release it after fetch
        with StreamManager.dataLock:
            # limit data fetch to 10000 byte at once
            end = min(StreamParser.seeker_position + 10000, len(StreamManager.rawData))
            #print(StreamManager.rawData)
            fetchedData = bytearray(StreamManager.rawData[StreamParser.seeker_position:end])

        # scan fetched data
        for index in range(len(fetchedData)):
            #print("index:",index,"fetch data:",fetchedData)
            byte = fetchedData[index]
            # parse line by line
            if byte == ord(b'\n'):
                package = StreamParser.rawPackage.decode('ascii')
                StreamParser.rawPackage.clear()
                if (package.startswith("$RQOBS")and not package.__contains__("FARduino")):
                    split_package = package.split(',')
                    hours   =   float(split_package[1][0:2])
                    minutes =   float(split_package[1][2:4])
                    seconds =   float(split_package[1][4:])
                    time_in_s = seconds+minutes*60+hours*3600
                    time.append(time_in_s)
                    channelValues[0].append(float(split_package[2]))
                    channelValues[1].append(float(split_package[3]))     
            else:
                StreamParser.rawPackage.append(fetchedData[index])
            StreamParser.seeker_position += 1

        # append parsed data to the global numerical data array
        with StreamManager.numDataLock:
            StreamManager.numData[0].extend(time)
            for chnNum in range(1,len(channelValues)+1,1):
                StreamManager.numData[chnNum].extend(channelValues[chnNum-1])