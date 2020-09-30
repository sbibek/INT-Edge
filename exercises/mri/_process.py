import os

class ProcessMetrics:
    def __init__(self):
       self.perHopStats = {}
       self.linkLatency = {}

    def process(self, _data):
        for data in _data:
            swid, qdepth, hopLatency, linkLatency = data
            self.perHopStats[swid] = {"qdepth": qdepth, "hopLatency": hopLatency}

        for i in range(1, len(_data)):
            _from = _data[i-1]
            _to = _data[i]
            key = (_from[0], _to[0])
            self.linkLatency[key] = _to[3]
        
        self.__log()
    
    def __log(self):
        os.system('clear')
        for key in self.perHopStats:
            print "swid: {}, qdepth: {}, hopLatency: {} microsecs".format(key, self.perHopStats[key]["qdepth"], self.perHopStats[key]["hopLatency"])

        for key in self.linkLatency:
            print "{}->{} linklatency: {} microsecs ".format(key[0], key[1], self.linkLatency[key])
