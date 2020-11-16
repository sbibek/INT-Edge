from scapy.all import sniff, packet
from scapy.all import IP, UDP
import struct

class ProbeListener:
    def __init__(self, listenerConf, processor):
        self.conf = listenerConf
        self.processor = processor
    
    def handleIncomingPacket(self, pkt):
        if not (UDP in pkt and pkt[UDP].dport == self.conf['port']):
            print("not UDP packet or port is not standard")
            return
        
        # now we extract the information on this packet
        format = ">IIIIIIIII"
        messageLen = 36
        linkinfolen = 9

        payload = pkt[UDP].payload.load
        fork, hops = struct.unpack(">HH",payload[0:4])
        # print "path: {}, total hops: {}".format(fork, hops)
        payload = payload[4:]

        data = []
        for i in range(hops):
            hop = struct.unpack(format,payload[:messageLen])
            payload = payload[messageLen:]

            linkinfo = {}
            for i in range(linkinfolen):
                sw, ldelay, mldelay  = struct.unpack(">III", payload[i*12:(i+1)*12])
                linkinfo[sw] = (ldelay, mldelay)

            data.insert(0, [hop, linkinfo])
            payload = payload[108:]
        
        # send it to telemetry processor
        self.processor.process(data)

 
    def start(self):
        sniff(filter='udp and dst port {}'.format(self.conf['port']), iface=self.conf['interface'], prn=self.handleIncomingPacket, store=False)

