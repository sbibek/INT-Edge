#!/usr/bin/env python

import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP, Raw
from scapy.all import IntField, FieldListField, FieldLenField, ShortField, PacketListField
from scapy.layers.inet import _IPOption_HDR

from time import sleep

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface


def getPacket(iface, addr, path):
    return Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") / IP(
        dst=addr)/ UDP(
            dport=4321, sport=1234) / Raw(load=struct.pack('>HH', path, 0)) 



def main():
    if len(sys.argv)<2:
        print 'pass 2 arguments: <destination> "<no of messages>"'
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    try:
      for i in range(int(sys.argv[2])):
        sendp(getPacket(iface, addr, 0), iface=iface)
        sleep(1)
        # sendp(getPacket(iface, addr, 1), iface=iface)
    except KeyboardInterrupt:
        raise


if __name__ == '__main__':
    main()
