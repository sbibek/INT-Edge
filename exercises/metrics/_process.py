import os

class ProcessMetrics:
    def __init__(self):
       self.perHopStats = {}
       self.linkLatency = {}
       self.totalProbes = 0
       self.totalUpdateTime = 0

    def process(self, _data, diff):
        self.totalProbes += 1
        self.totalUpdateTime += diff
        for data in _data:
            swid, qdepth, hopLatency, linkLatency = data
            if swid in self.perHopStats:
                r = self.perHopStats[swid]
                self.perHopStats[swid] = {"qdepth": {'latest':qdepth, 'total': r['qdepth']['total'] + qdepth}, "hopLatency": {'latest':hopLatency, 'total': r['hopLatency']['total'] + hopLatency}}
            else:
                self.perHopStats[swid] = {"qdepth": {'latest':qdepth, 'total': 0}, "hopLatency": {'latest':hopLatency, 'total': 0}}

        for i in range(1, len(_data)):
            _from = _data[i-1]
            _to = _data[i]
            key = (_from[0], _to[0])
            if key in self.linkLatency:
                r = self.linkLatency[key]
                self.linkLatency[key] = { 'latest':_to[3], 'total': r['total'] + _to[3]}
            else:
                self.linkLatency[key] = { 'latest':_to[3], 'total': 0}
        
        self.__log(diff)
    
    def __log(self, diff):
        os.system('clear')
        print('total probes {}, last updated {}s (avg {}s)'.format(self.totalProbes, diff, self.totalUpdateTime/self.totalProbes))
        for key in self.perHopStats:
            print "swid: {}, qdepth: {} (avg: {}), hopLatency: {} microsecs (avg: {})".format(key, self.perHopStats[key]["qdepth"]["latest"], self.perHopStats[key]["qdepth"]["total"]//self.totalProbes, self.perHopStats[key]["hopLatency"]["latest"], self.perHopStats[key]["hopLatency"]["total"]//self.totalProbes)

        for key in self.linkLatency:
            print "{}->{} linklatency: {} microsecs(avg: {}) ".format(key[0], key[1], self.linkLatency[key]['latest'], self.linkLatency[key]['total']/self.totalProbes)
