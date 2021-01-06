from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteSSHLink as RemoteLink )
# ^ Could also use: RemoteSSHLink, RemoteGRELink
from mininet.topolib import TreeTopo
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.examples.clustercli import ClusterCLI


from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

CLUSTER = True

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2, lossy=True ):
        switch = self.addSwitch('s1')
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1),
                                cpu=.5 / n)
            if lossy:
                # 10 Mbps, 5ms delay, 10% packet loss
                self.addLink(host, switch,
                             bw=100, delay='10ms', loss=10, use_htb=True)
            else:
                # 10 Mbps, 5ms delay, no packet loss
                self.addLink(host, switch,
                             bw=100, delay='10ms', loss=0, use_htb=True)

def demo():
    "Simple Demo of Cluster Mode"
    servers = [ 'localhost', 'localhost' ]
    topo = SingleSwitchTopo( n=2, lossy=True )

    if CLUSTER:
        net = MininetCluster( topo=topo, servers=servers, link=RemoteLink,
                            placement=SwitchBinPlacer )
        net.start()
        ClusterCLI( net )        
        net.stop()
    else:
        net = Mininet( topo=topo, link=TCLink)
        net.start()
        CLI( net )
        net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    demo()