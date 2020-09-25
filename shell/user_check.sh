#/bin/bash
set -xu

ip=$(ifconfig eth0|awk 'NR==2{print$2}')
port=80
for ((i=0;i<40;i++))
do
	user_num=$(netstat -ant|grep $ip:$port|grep "ESTABLISHED"|wc -l)
	if [ $user_num -eq 0 ];then
		exit 0
	else
		echo "Current number of user connections: $user_num"
		sleep 3
	fi
done
echo "User connection not disconnected: $user_num"
exit 1