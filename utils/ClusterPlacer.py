from mininet.examples.cluster import Placer


def getP4CustomPlacer(clusterinfo):
    class P4ClusterPlacer(Placer):
        def __init__( self, *args, **kwargs ):
            Placer.__init__( self, *args, **kwargs )
            self.clusterinfo = clusterinfo
            print(self.clusterinfo)

        def __findServer(self, node):
            # first we need to find in the placer where this belongs
            for servalias in self.clusterinfo['placement']:
                if node in self.clusterinfo['placement'][servalias]:
                    return self.clusterinfo['servers'][servalias]

            return 'localhost'

        def place( self, node ):
            placed = self.__findServer(node)
            print "[Nodes Placement]{} placed in {}".format(node, placed)
            return placed
    
    return P4ClusterPlacer