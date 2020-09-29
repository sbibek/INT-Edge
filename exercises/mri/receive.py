#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import PacketListField, ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

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

def perHopPayload(data):
    print "switch id: {}, qdepth: {}, hop latency: {}".format(*data)


def handle_pkt(pkt):
    format = ">III"
    messageLen = 12

    payload = pkt[UDP].payload.load
    hops = struct.unpack(">H",payload[0:2])[0]
    payload = payload[2:]

    for i in range(hops):
        perHopPayload(struct.unpack(format,payload[:messageLen]))
        payload = payload[messageLen:]
#    hexdump(pkt)
    print "--------------------------------------------------"
    sys.stdout.flush()


def main():
    iface = 'eth0'
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(filter="udp and port 4321", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
