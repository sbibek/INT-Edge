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
        self.rolling_max_hoplatency = {}
        self.rolling_min_hoplatency = {}
        self.rolling_max_qdepth = {}
        self.rolling_min_qdepth = {}

        self.RtotalPackets = {}

        self.currentState = {"hop":{}, "link":{}}

        self.__initLogger()
        # self.log_ = [open('/home/bibek/xyz1.csv', 'w'), open('/home/bibek/xyz2.csv','w')]

    def csvlog(self, swid, type, data):
        lg = open('/home/bibek/sw-{}-{}.csv'.format(swid, type), 'a')
        strdata = ','.join(map(str, data)) 
        lg.write("{}\n".format(strdata))
        lg.close()


    def process(self, _data):
        try:
            for data in _data:
                swid, totalPackets, totalHopLatency, totalQdepth, max_hop_latency, min_hop_latency, max_qdepth, min_qdepth = data[0]

                if totalPackets == 0:
                    continue

                linkinfo = data[1]

                # avgHopLatency = round(totalHopLatency/(totalPackets*1.0),4)
                avgHopLatency = totalHopLatency
                avgQOccu = totalQdepth

                if swid not in self.switches:
                    self.switches.append(swid)

                if swid not in self.rolling_avgq:
                    self.rolling_avgq[swid] = RollingQ()
                self.rolling_avgq[swid].push(avgQOccu)

                if swid not in self.rolling_avghop:
                    self.rolling_avghop[swid] = RollingQ()
                self.rolling_avghop[swid].push(avgHopLatency)

                if swid not in self.rolling_max_hoplatency:
                    self.rolling_max_hoplatency[swid] = RollingQ()
                self.rolling_max_hoplatency[swid].push(max_hop_latency)

                if swid not in self.rolling_min_hoplatency:
                    self.rolling_min_hoplatency[swid] = RollingQ()
                self.rolling_min_hoplatency[swid].push(min_hop_latency)

                if swid not in self.rolling_max_qdepth:
                    self.rolling_max_qdepth[swid] = RollingQ()
                self.rolling_max_qdepth[swid].push(max_qdepth)

                if swid not in self.rolling_min_qdepth:
                    self.rolling_min_qdepth[swid] = RollingQ()
                self.rolling_min_qdepth[swid].push(min_qdepth)

                if swid not in self.RtotalPackets:
                    self.RtotalPackets[swid] = RollingQ()
                self.RtotalPackets[swid].push(totalPackets)

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
        os.system('clear')
        for swid in self.switches:
            # pps = self.rolling_pps[swid].avg()
            qoccupancy = self.rolling_avgq[swid].lastRolledValue
            hop = self.rolling_avghop[swid].lastRolledValue
            max_hop = self.rolling_max_hoplatency[swid].lastRolledValue
            min_hop = self.rolling_min_hoplatency[swid].lastRolledValue
            max_qdepth = self.rolling_max_qdepth[swid].lastRolledValue
            min_qdepth = self.rolling_min_qdepth[swid].lastRolledValue
            total_packets = self.RtotalPackets[swid].lastRolledValue


            if qoccupancy == -1:
                return
            
            logd = [total_packets, qoccupancy, min_qdepth, max_qdepth, hop, min_hop, max_hop]

            self.currentState["hop"][swid] = {"qoccupancy": qoccupancy, "hoplatency": hop, "maxhop": max_hop, "minhop":min_hop, "congestionlevel": self.congestionLevel(qoccupancy)}

            print("switch Id: {}, total packets: {}".format(swid, total_packets))
            print('     Queue occupancy: {} [{}, {}], hop latency: {} [{}, {}] microseconds'.format(qoccupancy, min_qdepth, max_qdepth, hop, min_hop, max_hop))
            print('')

            self.csvlog(int(swid),'hop', logd)

        # print("link latencies ")
        for k in self.rolling_linklatency:
            avg = self.rolling_linklatency[k].lastRolledValue
            if avg > 0.0:
                self.currentState["link"][k] = {"max": avg}
                print('     {} : avg: {}  (microseconds)'.format(k, avg))
                self.csvlog(k.replace('>', '-'), 'link', [avg])
        
        # self.csvlog(int(swid))
        
    
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
        
