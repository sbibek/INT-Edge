while true
do
	iperf3 -c $1 -t $2
	sleep $3
done
