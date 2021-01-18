sudo kill -9 $(ps -aux |grep mininet --line-buffered|awk '{print $2}')
