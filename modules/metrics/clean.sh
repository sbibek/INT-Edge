#!/bin/bash
echo "refershing build dir"
rm -rf ~/build
mkdir ~/build
echo "cleaning all"
make clean
mkdir logs pcaps
echo "retrive build dir"
sftp bibek@134.197.95.162:lab/p4int/modules/metrics/build/* ~/build/
echo "done"

