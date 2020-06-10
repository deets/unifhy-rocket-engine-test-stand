class appConfig:

    def __init__(self):
        self.isStacked = True
        self.isMultiAxis = False
        self.chnConfigs = []
        self.loadConfig()

    def loadConfig(self):
        path = "./Konfiguration/app.conf"
        with open(path,"r") as configFile:
            for line in configFile:
                line = line.replace(" ","").strip()
                configLine = line.split(':')
                # get isStacked
                if(configLine[0]=="isStacked"):
                    if configLine[1]=="True": 
                        self.isStacked=True
                    else:
                        self.isStacked=False
                # get isMultiAxis
                if(configLine[0]=="isMultiAxis"):
                    if configLine[1]=="True": 
                        self.isMultiAxis=True

                    else:
                        self.isMultiAxis=False

                # Channel config
                if(configLine[0]=="channel"):
                    self.chnConfigs.append(chnConfig(configLine[1], configLine[2], configLine[3],configLine[4],configLine[5]))
    
    def saveConfig(self):
        path = "./Konfiguration/app.conf"
        with open(path,"w") as configFile:
            configFile.write("isStacked : {}\n".format(self.isStacked))
            configFile.write("isMultiAxis : {}\n".format(self.isMultiAxis))
            for i in range(len(self.chnConfigs)):
                chn = self.chnConfigs[i]
                print("channel active: ",chn.__getattribute__("active"))
                configFile.write("channel : {0}:{1}:{2}:{3}:{4}\n".format(chn.title,chn.unit,chn.offset,chn.scale,chn.active))


    def changeConfig(self,chnNum,ctl,text):
        self.chnConfigs[chnNum-1].__setattr__(ctl,text)
        print("change Config",self.chnConfigs[chnNum-1].__getattribute__(ctl),ctl,text)
    
    def changeGraphLayout(self,isStacked):
        self.isStacked = isStacked

class chnConfig:

    def __init__(self,title,unit,offset,scale,active):
        self.title = title
        self.unit = unit
        self.offset = offset
        self.scale = scale
        self.active = active

    