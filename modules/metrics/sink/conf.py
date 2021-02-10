import json

class Configuration:
    def __init__(self, file='conf.json'):
        self.conf = None
        self.file = file
        self.__load()
    
    def __load(self):
        with open(self.file) as cf:
            self.conf = json.load(cf)
    
    def getListenConf(self):
        return self.conf['listen']
    
    def getMetaServerConf(self):
        return self.conf['metaserver']

    def getPeriod(self):
        return self.conf["period"]

# instantiate a variable
conf = Configuration()