import threading
import time
import os
from RollingQ import RollingQ

class Metrics(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.total_reported = 0

        
        # self.log = {1:open('/home/p4/logs/tcp/combined/1.csv', 'a'),2:open('/home/p4/logs/tcp/combined/2.csv', 'a')}
        self.switches = []


        self.rolling_pps = {}
        self.rolling_avgq = {}
        self.rolling_avghop = {}
        self.rolling_linklatency = {}
        self.rolling_minlinklatency = {}
    
    
    def process(self, _data, diff):
        for data in _data:
            swid, totalPackets, elapsedTime, totalHopLatency, minHopLatency, maxHopLatency, totalQdepth, minQdepth, maxQdepth = data[0]
            linkinfo = data[1]
            et = round(elapsedTime/(1000000.0),3)
            avgHopLatency = round(totalHopLatency/(totalPackets*1.0),4)
            avgQOccu, minQ, maxQ = round(totalQdepth/(totalPackets * 64.0)*100,3), round(minQdepth/64.0*100,2), round(maxQdepth/64.0*100,2)

            if swid not in self.switches:
                self.switches.append(swid)

            if swid not in self.rolling_pps:
                self.rolling_pps[swid] = RollingQ()
            self.rolling_pps[swid].push(round(totalPackets/et,2))

            if swid not in self.rolling_avgq:
                self.rolling_avgq[swid] = RollingQ()
            self.rolling_avgq[swid].push(avgQOccu)

            if swid not in self.rolling_avghop:
                self.rolling_avghop[swid] = RollingQ()
            self.rolling_avghop[swid].push(avgHopLatency)

            for key in linkinfo:
                _k = '{}->{}'.format(key, swid)
                if _k not in self.rolling_linklatency:
                    self.rolling_linklatency[_k] = RollingQ()
                self.rolling_linklatency[_k].push(linkinfo[key][0])

                if _k not in self.rolling_minlinklatency:
                    self.rolling_minlinklatency[_k] = RollingQ()
                self.rolling_minlinklatency[_k].push(linkinfo[key][1])


            # print "swid: {} ({}), total packets: {}, elapsed time: {}s ({})".format(swid, self.congestionLevel(avgQOccu), totalPackets, et, self.total_reported)
            # print "     Avg hop latency(microsec): {}, min: {}, max: {}".format(avgHopLatency, minHopLatency, maxHopLatency)
            # print "     Avg Q occupany(%): {}, min: {}, max: {}".format(avgQOccu, minQ, maxQ)
            # print "         Link information (Avg):"
            # for key in linkinfo:
            #     if linkinfo[key] != 0:
            #         print "             {} -> {}  {} microsecs".format(key, swid, linkinfo[key])

            # self.log[swid].write("{}, {}, {}, {}, {}, {}, {}, {}\n".format(totalPackets, et, avgHopLatency, minHopLatency, maxHopLatency, avgQOccu, minQ, maxQ))
        
        # if(self.total_reported >= 140): 
        #     self.log[1].close()
        #     self.log[2].close()
        #     exit(0)
        
        
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
    
    def generateMetrics(self):
        os.system('clear')
        for swid in self.switches:
            pps = self.rolling_pps[swid].avg()
            qoccupancy = self.rolling_avgq[swid].avg()
            hop = self.rolling_avghop[swid].avg()

            if pps == -1:
                return

            print "switch Id: {}, status: {}, pps: {}".format(swid, self.congestionLevel(qoccupancy), pps)
            print '     Queue occupancy: {}%, hop latency: {} microseconds'.format(qoccupancy, hop)
            print ''

        print "link latencies "
        for k in self.rolling_linklatency:
            avg = self.rolling_linklatency[k].avg()
            avgm = self.rolling_minlinklatency[k].avg()
            if avg > 0.0:
                print '     {} : min: {}, max: {}  (microseconds)'.format(k, avgm, avg)

        

    def __log(self, totalProbes, totalUpdateTime, current ):
        os.system('clear')
        print('total probes {}, avg update interval {}s'.format(totalProbes, totalUpdateTime/totalProbes))

        for swid in current:
            print "swid : {}".format(swid)
            print "     qdepth avg: {}, min: {}, max: {}".format(current[swid]["qdepth"]["avg"],current[swid]["qdepth"]["min"],current[swid]["qdepth"]["max"])
            print "     hop latency avg: {}, min: {}, max: {}".format(current[swid]["hoplatency"]["avg"],current[swid]["hoplatency"]["min"],current[swid]["hoplatency"]["max"])
        
      


    def run(self):

        try:
            while True:
                time.sleep(1)
                self.generateMetrics()
                
        
        except KeyboardInterrupt:
            pass