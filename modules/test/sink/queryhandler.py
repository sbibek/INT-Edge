from paths import paths, nstate

class QueryHandler:
    def __init__(self, processor):
        self.processor = processor
    
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

    def __resolveLink(self, link,  a, b):
        k1, k2 = "{}->{}".format(a,b), "{}->{}".format(b,a)
        if k1 in link:
            return link[k1]
        elif k2 in link:
            return link[k2]
        else:
            return None

                