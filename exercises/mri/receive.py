#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import PacketListField, ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

from _process import ProcessMetrics


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
    global lastTime
    diff = 0
    if lastTime == None:
        lastTime = time.time()
    else:
        curr = time.time()
        diff = curr - lastTime
        lastTime = curr

    format = ">IIII"
    messageLen = 16

    payload = pkt[UDP].payload.load
    fork, hops = struct.unpack(">HH",payload[0:4])
    # print "path: {}, total hops: {}".format(fork, hops)
    payload = payload[4:]

    data = []
    for i in range(hops):
        data.insert(0, struct.unpack(format,payload[:messageLen]))
        payload = payload[messageLen+6:]
#    hexdump(pkt)
    processor.process(data, diff)
    sys.stdout.flush()


def main():
    iface = 'eth0'
    processMetrics = ProcessMetrics()
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(filter="udp and port 4321", iface = iface,
          prn = lambda x: handle_pkt(x, processMetrics))

if __name__ == '__main__':
    main()
