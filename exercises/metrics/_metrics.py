import threading
import time
import os
from RollingQ import RollingQ
import logging

class Node:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.next = None
        self.prev = None

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

        self.currentState = {"hop":{}, "link":{}}
        self.count = 0
    
    
    def process(self, _data, diff):
        try:
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
            self.count += 1
        except Exception as e:
            logging.error('Error at %s', 'division', exc_info=e)


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
    
    def getLinksStartingFrom(self, links, swid):
        r = []
        for k in links:
            if k.startswith(str(swid)):
                r.append((k, links[k]))
        return r

    
    def sortNodes(self, ref):
        nodes = {}
        hops = [1,2,3,5, 4,6]
        for hop in hops:
            links = self.getLinksStartingFrom(self.currentState["link"], str(hop))
            for link in links:
                linkhops = link[0].split('->')
                if int(linkhops[0]) == 1:
                    # if from the first node itself
                    nodes[linkhops[1]] = link[1]["max"] + self.currentState["hop"][int(linkhops[0])]['hoplatency']
                else:
                    if linkhops[1] not in nodes:
                    # we have to look back to the previous values
                        nodes[linkhops[1]] = nodes[linkhops[0]] + link[1]["max"] + self.currentState["hop"][int(linkhops[0])]['hoplatency']
        
        n = []
        for node in nodes:
            n.append((node, nodes[node]))
        n.sort(key = lambda x:x[1])
        print n

        
    def generateMetrics(self):
        # os.system('clear')
        print(" count {}".format(self.count))
        for swid in self.switches:
            pps = self.rolling_pps[swid].avg()
            qoccupancy = self.rolling_avgq[swid].avg()
            hop = self.rolling_avghop[swid].avg()

            if pps == -1:
                return
            
            self.currentState["hop"][swid] = {"qoccupancy": qoccupancy, "hoplatency": hop, "congestionlevel": self.congestionLevel(qoccupancy), "pps": pps}

            print "switch Id: {}, status: {}, pps: {}".format(swid, self.congestionLevel(qoccupancy), pps)
            print '     Queue occupancy: {}%, hop latency: {} microseconds'.format(qoccupancy, hop)
            print ''

        print "link latencies "
        for k in self.rolling_linklatency:
            avg = self.rolling_linklatency[k].avg()
            avgm = self.rolling_minlinklatency[k].avg()
            if avg > 0.0:
                self.currentState["link"][k] = {"min": avgm, "max": avg}
                print '     {} : min: {}, max: {}  (microseconds)'.format(k, avgm, avg)
        
        self.sortNodes(ref=1)

        

    def __log(self, totalProbes, totalUpdateTime, current ):
        os.system('clear')
        print('total probes {}, avg update interval {}s'.format(totalProbes, totalUpdateTime/totalProbes))

        for swid in current:
            print "swid : {}".format(swid)
            print "     qdepth avg: {}, min: {}, max: {}".format(current[swid]["qdepth"]["avg"],current[swid]["qdepth"]["min"],current[swid]["qdepth"]["max"])
            print "     hop latency avg: {}, min: {}, max: {}".format(current[swid]["hoplatency"]["avg"],current[swid]["hoplatency"]["min"],current[swid]["hoplatency"]["max"])
        
      


    def run(self):
        while True:
            time.sleep(1)
            try:
                self.generateMetrics()
            except Exception as e:
                    logging.error('Error at %s', 'division', exc_info=e)
                
  