from paths import paths, pathsWithEgress, nstate

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

        if qocc == 0:
            return bwusage
        elif qocc <= 1:
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

    def rankIV(self, wrt=1):
        state = self.processor.getCurrentSnapshot()
        # state = nstate
        hopinfo = state['hop']
        link = state['link']      

        pathinfo = pathsWithEgress[wrt]


        for destination in pathinfo:
            lasthop = -1
            hop = True
            for p in pathinfo[destination]:
                if hop == True:
                    if lasthop != -1:
                        # then there is a pair link so make it
                        linkab = self.__resolveLink(link, lasthop, p)
                        print("D({}->{}) = {}".format(lasthop, p, linkab['max']))                    
                    # now make this the last hop that was encountered
                    lasthop = p
                else:
                    # means this is a port of lasthop
                    q = self.__getEgressPortQueue(hopinfo, lasthop, p)
                    print("Q({}::{}) = {}".format(lasthop, p, q))
                
                hop = True if hop is False else False
        return [(1,2), (3,4)]



    def __getEgressPortQueue(self,hopinfo, hop, port):
        qinfo = hopinfo[hop]["egressQ"][port]
        return qinfo


    def __resolveLink(self, link,  a, b):
        k1, k2 = "{}->{}".format(a,b), "{}->{}".format(b,a)
        if k1 in link:
            return link[k1]
        elif k2 in link:
            return link[k2]
        else:
            return None

                