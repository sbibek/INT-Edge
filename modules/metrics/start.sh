#!/bin/bash

cd ~/lab/p4int/modules/metrics

screen -dmS mininet bash -c "make clean && make && bash"
screen -r mininet
