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
        messageLen = 11 
        linkinfolen = 5 

        payload = pkt[UDP].payload.load
        fork, hops = struct.unpack(">HH",payload[0:4])
        payload = payload[4:]

        data = []
        for i in range(hops):
            hop = struct.unpack(">BIIH",payload[:messageLen])
            payload = payload[messageLen:]

            linkinfo = {}
            for i in range(linkinfolen):
                sw, ldelay  = struct.unpack(">BH", payload[i*3:(i+1)*3])
                if ldelay > 0:
                    linkinfo[sw] = (ldelay, 0)

            
            payload = payload[15:]
            # now per port queue status at egress
            # we have 5 values
            egress_q = struct.unpack( ">IIIII", payload[:20])
            data.insert(0, [hop, linkinfo, egress_q])
            payload = payload[20:]


        # send it to telemetry processor
        self.processor.process(data)

 
    def start(self):
        sniff(filter='udp and dst port {}'.format(self.conf['port']), iface=self.conf['interface'], prn=self.handleIncomingPacket, store=False)

