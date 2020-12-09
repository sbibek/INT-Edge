from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch
from mininet.examples.cluster import RemoteMixin

class RemoteP4Host(RemoteMixin, P4Host):
    pass