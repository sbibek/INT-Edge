import threading
import time
import os

class Metrics(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.total_reported = 0

        self.log = {1:open('/home/p4/logs/1.csv', 'a'),2:open('/home/p4/logs/2.csv', 'a')}
    
    
    def process(self, _data, diff):
        self.total_reported += 1
        os.system('clear')
        for data in _data:
            swid, totalPackets, elapsedTime, totalHopLatency, minHopLatency, maxHopLatency, totalQdepth, minQdepth, maxQdepth = data
            et = round(elapsedTime/(1000000.0),3)
            avgHopLatency = round(totalHopLatency/(totalPackets*1.0),4)
            avgQOccu, minQ, maxQ = round(totalQdepth/(totalPackets * 64.0)*100,3), round(minQdepth/64.0*100,2), round(maxQdepth/64.0*100,2)
            print "swid: {}, total packets: {}, elapsed time: {}s ({})".format(swid, totalPackets, et, self.total_reported)
            print "     Avg hop latency(microsec): {}, min: {}, max: {}".format(avgHopLatency, minHopLatency, maxHopLatency)
            print "     Avg Q occupany(%): {}, min: {}, max: {}".format(avgQOccu, minQ, maxQ)
            self.log[swid].write("{}, {}, {}, {}, {}, {}, {}, {}\n".format(totalPackets, et, avgHopLatency, minHopLatency, maxHopLatency, avgQOccu, minQ, maxQ))
        
        if(self.total_reported >= 100): 
            self.log[1].close()
            self.log[2].close()
            exit(0)
        
        
    
    def generateMetrics(self):
        pass
        

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
                time.sleep(0.05)
                self.generateMetrics()
            except:
                break