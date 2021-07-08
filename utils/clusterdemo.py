#!/usr/bin/python

"clusterdemo.py: demo of Mininet Cluster Edition prototype"

from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteLink )
# ^ Could also use: RemoteSSHLink, RemoteGRELink
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.examples.clustercli import ClusterCLI as CLI

def demo():
    "Simple Demo of Cluster Mode"
    servers = [ 'localhost', '134.197.42.31' ]
    topo = TreeTopo( depth=2, fanout=2 )
    net = MininetCluster( topo=topo, servers=servers, link=RemoteLink,
                          placement=SwitchBinPlacer )
    net.start()
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    demo()
