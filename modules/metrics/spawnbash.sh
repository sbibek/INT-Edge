#!/bin/bash

cd ~/lab/p4int/modules/metrics
hpid=$(ps -aux | grep "bash --norc --noediting -is mininet:h$1" --line-buffered|awk '{print $2;exit}')
echo "[spawn bash] spawning bash for the host $var with pid $hpid"
screen -dmS "b-h$1" bash -c "sudo nsenter -t $hpid -n bash"
screen -r "b-h$1"
