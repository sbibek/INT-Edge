#!/bin/bash

cd ~/lab/p4int/modules/metrics

	hpid=$(ps -aux | grep "00 bash --norc --noediting -is mininet:h6" --line-buffered|awk '{print $2;exit}')
	echo "[spawnhost] spawning host $var with pid $hpid"
	screen -dmS "h$var" bash -c "sudo nsenter -t $hpid -n bash sink.sh"
