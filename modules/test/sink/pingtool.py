import json
from textwrap import dedent
import pingparsing

import subprocess

def log(file, data):
    lg = open('/home/bibek/{}.csv'.format(file), 'a')
    strdata = ','.join(map(str, data)) 
    lg.write("{}\n".format(strdata))
    lg.close()

def ping(host, count, title):
    ping_response = subprocess.Popen(["/bin/ping", "-c{}".format(count), host], stdout=subprocess.PIPE).stdout.read()

    parser = pingparsing.PingParsing()
    stats= parser.parse(dedent(ping_response.decode()))
    # print(stats['rtt_min'])
    # print("[extract ping statistics]")
    r = json.loads(json.dumps(stats.as_dict(), indent=4))
    d = [title, r['rtt_avg'], r['rtt_min'], r['rtt_max'], r['rtt_mdev']]

    log('rtt-log', d)
    return d

    # print("\n[extract icmp replies]")
    # for icmp_reply in stats.icmp_replies:
    #     print(icmp_reply)


print(ping('192.168.2.10',120, 'rtt-100'))