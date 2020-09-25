#/bin/bash
set -xu
for ((i=0;i<20;i++))
do
	status_code=`curl -s -w "%{http_code}" -m 5 $(curl -s cip.cc|awk '/IP/{print$3}')/ping -o /dev/null`
	if [ $status_code -eq "200" ];then
		exit 0
	else
		sleep 3
		echo "HTTP Survival detection error"
	fi
done
exit 1