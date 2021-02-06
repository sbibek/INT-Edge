import logging
import threading
import time
import os
from RollingQ import RollingQ

class TelemetryProcessor:
    def __init__(self):
        self.stopLogging = False
        self.switches = []
        self.rolling_pps = {}
        self.rolling_avgq = {}
        self.rolling_avghop = {}
        self.rolling_linklatency = {}
        self.egressQ = {}

        self.currentState = {"hop":{}, "link":{}}

        self.printenabled = False

        self.__initLogger()

        
        # self.log_ = [open('/home/bibek/xyz1.csv', 'w'), open('/home/bibek/xyz2.csv','w')]

    def csvlog(self, i, data):
        pass
        # lg = open('/home/bibek/xyz{}.csv'.format(i), 'a')
        # lg.write("{}\n".format(data))
        # lg.close()


    def process(self, _data):
        try:
            for data in _data:
                swid, totalPackets, totalHopLatency, totalQdepth = data[0]

                if totalPackets == 0:
                    continue

                linkinfo = data[1]
                egressQueueInfo = data[2]

                avgHopLatency = round(totalHopLatency/(totalPackets*1.0),4)
                avgQOccu = totalQdepth

                if swid not in self.switches:
                    self.switches.append(swid)

                if swid not in self.rolling_avgq:
                    self.rolling_avgq[swid] = RollingQ()
                self.rolling_avgq[swid].push(avgQOccu)

                if swid not in self.rolling_avghop:
                    self.rolling_avghop[swid] = RollingQ()
                self.rolling_avghop[swid].push(avgHopLatency)

                # if swid not in self.egressQ:
                self.egressQ[swid] = egressQueueInfo
                

                for key in linkinfo:
                    _k = '{}->{}'.format(key, swid)
                    if _k not in self.rolling_linklatency:
                        self.rolling_linklatency[_k] = RollingQ()
                    self.rolling_linklatency[_k].push(linkinfo[key][0])
# 
        except Exception as e:
            logging.error('Error at %s', 'division', exc_info=e)
    

    def congestionLevel(self, avg):
        if avg == 0:
            return "NO_CONGESTION"
        elif avg <= 5:
            return "LOW_CONGESTION"
        elif avg <= 10:
            return "MED_CONGESTION"
        elif avg <= 25:
            return "CONGESTED"
        else:
            return "HIGH_CONGESTION"
    
    def log(self):
        if self.printenabled == True:
            os.system('clear')

        for swid in self.switches:
            # pps = self.rolling_pps[swid].avg()
            qoccupancy = self.rolling_avgq[swid].lastRolledValue
            hop = self.rolling_avghop[swid].lastRolledValue

            if qoccupancy == -1:
                return
            
            self.currentState["hop"][swid] = {"qoccupancy": qoccupancy, "hoplatency": hop, "congestionlevel": self.congestionLevel(qoccupancy), "egressQ": self.egressQ[swid]}
            if self.printenabled == True:
                print("switch Id: {}".format(swid))
                print('     Queue occupancy: {} ({}), hop latency: {} microseconds'.format(qoccupancy, self.egressQ[swid], hop))
                print('')

            # self.csvlog(int(swid),hop)

        # print("link latencies ")
        for k in self.rolling_linklatency:
            avg = self.rolling_linklatency[k].lastRolledValue
            if avg > 0.0:
                self.currentState["link"][k] = {"max": avg}
                if self.printenabled == True:
                    print('     {} : avg: {}  (microseconds)'.format(k, avg))
    
    def getCurrentSnapshot(self):
        return self.currentState
    
    def __initLogger(self):
        self.loggingThread = threading.Thread(target = self.loggerThread)
        self.loggingThread.start()
    
    def loggerThread(self):
        while not self.stopLogging:
            self.log()
            time.sleep(0.5)
    
    def stopLogging(self):
        self.stopLogging = True
        time.sleep(2)
        
