from paths import paths, nstate

class QueryHandler:
    def __init__(self, processor):
        self.processor = processor
        self.defaultHopValue = 1
        self.defaultLinkValue = 1
    
    def rank(self, wrt=1):
        state = self.processor.getCurrentSnapshot()
        # state = nstate
        hop = state['hop']
        link = state['link']

        pathinfo = paths[wrt]
        resolvedLatencies = []
        for destination in pathinfo:
            path = pathinfo[destination]
            latency = 0
            for (a,b) in path:
                linkab = self.__resolveLink(link, a, b)
                latency += ( hop[a]['hoplatency'] + linkab['max'] )
            latency += hop[destination]['hoplatency']
            resolvedLatencies.append((destination, latency))
        
        resolvedLatencies = sorted(resolvedLatencies, key=lambda x: x[1]) 
        return resolvedLatencies
    
    def rankII(self, wrt=1):
        state = self.processor.getCurrentSnapshot()
        # state = nstate
        hop = state['hop']
        link = state['link']

        # we will first rank on the basis of the queue occupancy
        pathinfo = paths[wrt]
        resolvedLatencies = []
        for destination in pathinfo:
            path = pathinfo[destination]
            latency = 0
            for (a,b) in path:
                linkab = self.__resolveLink(link, a, b)
                latency += ( hop[a]['qoccupancy']*20000 + linkab['max'])
            latency += hop[destination]['qoccupancy']*20000
            resolvedLatencies.append((destination, latency))
        
        resolvedLatencies = sorted(resolvedLatencies, key=lambda x: x[1]) 
        return resolvedLatencies 
    
    def bwusage(self, qocc):
        bwusage = 0
        if qocc > 0 and qocc <= 1:
            bwusage = 20
        elif qocc <= 4:
            bwusage =50
        elif qocc <= 24:
            bwusage = 80
        else:
            bwusage = 100
        return bwusage

    def rankIII(self, wrt=1):
        state = self.processor.getCurrentSnapshot()
        # state = nstate
        hop = state['hop']
        link = state['link']

        # we will first rank on the basis of the queue occupancy
        pathinfo = paths[wrt]
        resolvedLatencies = []
        for destination in pathinfo:
            path = pathinfo[destination]
            latency = 0
            for (a,b) in path:
                linkab = self.__resolveLink(link, a, b)
                usage =  self.bwusage(hop[a]['qoccupancy'])
                if usage > latency:
                    latency = usage
                    
            usage = self.bwusage(hop[destination]['qoccupancy'])
            if usage > latency:
                latency = usage
            resolvedLatencies.append((destination, latency))
        
        resolvedLatencies = sorted(resolvedLatencies, key=lambda x: x[1]) 
        return resolvedLatencies 




    def __resolveLink(self, link,  a, b):
        k1, k2 = "{}->{}".format(a,b), "{}->{}".format(b,a)
        if k1 in link:
            return link[k1]
        elif k2 in link:
            return link[k2]
        else:
            return None

                