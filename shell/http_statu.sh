#/bin/bash
set -xu
public_ip=$(curl -s cip.cc|awk '/IP/{printf$3}')
for ((i=0;i<20;i++))
do
	status_code=`curl -s -w "%{http_code}" -m 5 $public_ip/ping -o /dev/null`
	if [ $status_code -eq "200" ];then
		exit 0
	else
		sleep 3
		echo "HTTP Survival detection error"
	fi
done
exit 1