#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import PacketListField, ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

from _process import ProcessMetrics
from _metrics import Metrics


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

import time
lastTime = None
def handle_pkt(pkt, processor):
    if UDP not in pkt or ( pkt[UDP].sport != 4321 and pkt[UDP].dport != 4321):
        return

    global lastTime
    diff = 0
    if lastTime == None:
        lastTime = time.time()
    else:
        curr = time.time()
        diff = curr - lastTime
        lastTime = curr

    format = ">IIIIIIIII"
    messageLen = 36
    linkinfolen = 5 

    payload = pkt[UDP].payload.load

    fork, hops = struct.unpack(">HH",payload[0:4])
    # print "path: {}, total hops: {}".format(fork, hops)
    payload = payload[4:]

    data = []
    for i in range(hops):
        hop = struct.unpack(">BIIH",payload[:11])
        payload = payload[11:]

        linkinfo = {}
        for i in range(linkinfolen):
            sw, ldelay  = struct.unpack(">BH", payload[i*3:(i+1)*3])
            if ldelay > 0:
                linkinfo[sw] = (ldelay)
        
        data.insert(0, [hop, linkinfo])
        payload = payload[15:]

#    hexdump(pkt)
    # processor.process(data, diff)
    print data
    sys.stdout.flush()


def main():
    iface = 'eth0'
    processMetrics = Metrics()
    # processMetrics.start()
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(filter="udp and port 4321", iface = iface,
          prn = lambda x: handle_pkt(x, processMetrics))

if __name__ == '__main__':
    main()
