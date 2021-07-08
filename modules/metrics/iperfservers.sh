#!/bin/bash

cd ~/lab/p4int/modules/metrics

for var in "$@"
do
	hpid=$(ps -aux | grep "00 bash --norc --noediting -is mininet:h$var" --line-buffered|awk '{print $2;exit}')
	echo "[iperf server] spawning iperf server in the host $var with pid $hpid"
	screen -dmS "is-h$var" bash -c "sudo nsenter -t $hpid -n iperf3 -s"
done
