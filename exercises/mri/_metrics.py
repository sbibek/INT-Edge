import threading
import time
import os

class Metrics(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.history = [] 
        self.index = 0

        self.metrics = []

        self.totalUpdateTime = 0
    
    def process(self, _data, diff):
        entry = {}
        for data in _data:
            swid, qdepth, hopLatency, linkLatency = data
            entry[swid] = {"swid": swid, "qdepth": qdepth, "hoplatency": hopLatency, "linklatency":linkLatency}
        self.history.append(entry)
        self.totalUpdateTime += diff
    
    def generateMetrics(self):
        total = len(self.history)
        data = self.history[self.index:total]
        updatetime = self.totalUpdateTime
        self.totalUpdateTime = 0
        self.index = total

        current = {}
        for entry in data:
            for swid in entry:
                sinfo = entry[swid]
                if swid not in current:
                    current[swid] = {"hoplatency": {"max": sinfo["hoplatency"], "min": sinfo["hoplatency"], "total": 0, "avg": 0}, "qdepth": {"max": sinfo["qdepth"], "min": sinfo["qdepth"], "total": 0, "avg": 0} }

                # now lets update the details 
                instance = current[swid]
                instance["hoplatency"]["total"] += sinfo["hoplatency"]

                if sinfo["hoplatency"] > instance["hoplatency"]["max"]:
                    instance["hoplatency"]["max"] = sinfo["hoplatency"]

                if sinfo["hoplatency"] < instance["hoplatency"]["min"]:
                    instance["hoplatency"]["min"] = sinfo["hoplatency"]
                
                instance["qdepth"]["total"] += sinfo["qdepth"]

                if sinfo["qdepth"] > instance["qdepth"]["max"]:
                    instance["qdepth"]["max"] = sinfo["qdepth"]

                if sinfo["qdepth"] < instance["qdepth"]["min"]:
                    instance["qdepth"]["min"] = sinfo["qdepth"]
        
        if len(current) > 0:
            for swid in current:
                instance = current[swid]
                instance["hoplatency"]["avg"] = instance["hoplatency"]["total"] / len(data)
                instance["qdepth"]["avg"] = instance["qdepth"]["total"] / len(data)
            # self.metrics.append(current)
            self.__log(len(data), updatetime, current) 

    def __log(self, totalProbes, totalUpdateTime, current ):
        os.system('clear')
        print('total probes {}, avg update interval {}s'.format(totalProbes, totalUpdateTime/totalProbes))

        for swid in current:
            print "swid : {}".format(swid)
            print "     qdepth avg: {}, min: {}, max: {}".format(current[swid]["qdepth"]["avg"],current[swid]["qdepth"]["min"],current[swid]["qdepth"]["max"])
            print "     hop latency avg: {}, min: {}, max: {}".format(current[swid]["hoplatency"]["avg"],current[swid]["hoplatency"]["min"],current[swid]["hoplatency"]["max"])


    def run(self):
        while True:
            try:
                time.sleep(1)
                self.generateMetrics()
            except:
                break