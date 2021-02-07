#!/bin/bash

sudo tc qdisc del dev s1-eth1 root
sudo tc qdisc del dev s1-eth2 root
sudo tc qdisc del dev s2-eth1 root
sudo tc qdisc del dev s2-eth2 root
sudo tc qdisc del dev s7-eth1 root
sudo tc qdisc del dev s7-eth2 root
sudo tc qdisc del dev s7-eth3 root
sudo tc qdisc del dev s7-eth4 root
sudo tc qdisc add dev s1-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s1-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s2-eth1 root netem delay 10ms rate 7mbit
sudo tc qdisc add dev s2-eth2 root netem delay 10ms rate 7mbit
sudo tc qdisc add dev s7-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s7-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s7-eth3 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s7-eth4 root netem delay 10ms rate 8mbit

sudo tc qdisc del dev s5-eth1 root
sudo tc qdisc del dev s5-eth2 root
sudo tc qdisc del dev s6-eth1 root
sudo tc qdisc del dev s6-eth2 root
sudo tc qdisc del dev s8-eth1 root
sudo tc qdisc del dev s8-eth2 root
sudo tc qdisc del dev s8-eth3 root
sudo tc qdisc del dev s8-eth4 root
sudo tc qdisc add dev s5-eth1 root netem delay 10ms rate 7mbit
sudo tc qdisc add dev s5-eth2 root netem delay 10ms rate 7mbit
sudo tc qdisc add dev s6-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s6-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s8-eth1 root netem delay 10ms rate 6mbit
sudo tc qdisc add dev s8-eth2 root netem delay 10ms rate 6mbit
sudo tc qdisc add dev s8-eth3 root netem delay 10ms rate 6mbit
sudo tc qdisc add dev s8-eth4 root netem delay 10ms rate 6mbit

sudo tc qdisc del dev s3-eth1 root
sudo tc qdisc del dev s3-eth2 root
sudo tc qdisc del dev s4-eth1 root
sudo tc qdisc del dev s4-eth2 root
sudo tc qdisc del dev s9-eth1 root
sudo tc qdisc del dev s9-eth2 root
sudo tc qdisc del dev s9-eth3 root
sudo tc qdisc del dev s9-eth4 root
sudo tc qdisc add dev s3-eth1 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s3-eth2 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s4-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s4-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s9-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s9-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s9-eth3 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s9-eth4 root netem delay 10ms rate 8mbit

sudo tc qdisc del dev s11-eth1 root
sudo tc qdisc del dev s11-eth2 root
sudo tc qdisc del dev s12-eth1 root
sudo tc qdisc del dev s12-eth2 root
sudo tc qdisc del dev s10-eth1 root
sudo tc qdisc del dev s10-eth2 root
sudo tc qdisc del dev s10-eth3 root
sudo tc qdisc del dev s10-eth4 root
sudo tc qdisc add dev s11-eth1 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s11-eth2 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s12-eth1 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s12-eth2 root netem delay 10ms rate 5mbit
sudo tc qdisc add dev s10-eth1 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s10-eth2 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s10-eth3 root netem delay 10ms rate 8mbit
sudo tc qdisc add dev s10-eth4 root netem delay 10ms rate 8mbit

