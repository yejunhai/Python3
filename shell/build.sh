#bin/bash

set -e -u

export PATH=$PATH:/var/jenkins_home/tools/hudson.plugins.gradle.GradleInstallation/Gradle_4.8/bin/
back_dir=/var/jenkins_home/jobs/weather/builds/$version/archive/code/weather/weather-api/build/libs
hosts=wetaher
#jarfile=weather-api.jar
jarpath=/root/local/apps/weather-api
inventory=/inventory/$hosts.yaml

update(){
	 ansible $hosts[$1] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb.py stop"
     ansible $hosts[$1] -i $inventory -m copy -a "src=$build_dir/build/libs/ dest=$jarpath/"
     ansible $hosts[$1] -i $inventory -m shell -a "cd $jarpath;sh server.sh stop"
     ansible $hosts[$1] -i $inventory -m shell -a "cd $jarpath;sh server.sh start"
}

case $deployment_selection in

deploy)
     echo "begin $deployment_selection "
     cd  $build_dir
     gradle clean build -x test -Penv=pro
     update 0
     exit 0
     ;;

rollback)
     echo "begin $deployment_selection  version=$version"
     if [ $version -eq 0 ];then
		echo "Version not specified"
		exit 1
	 fi
     rm -rf $build_dir/build/libs
     cp -rp /var/jenkins_home/workspace/weather/code/weather/weather-api $build_dir/build/
     cd $build_dir/build/libs && ls || exit 1
     update 0
     ansible $hosts[0] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb.py start"
     exit 0
     ;;

all_deploy)
	echo "begin $deployment_selection  version=$version"
	if [ $version -eq 0 ];then
		echo "Version not specified"
		exit 1
	fi
	rm -rf $build_dir/build/libs
	cp -rp /var/jenkins_home/workspace/weather/code/weather/weather-api $build_dir/build/
	cd $build_dir/build/libs && ls || exit 1
	host_number=$(grep -v "^\[" $inventory |wc -l)
	for ((i=0;i<$host_number;i++))
	do
		update $i
	    ansible $hosts[$i] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb.py start"
	done
	exit 0
	;;

   *)
    exit 1
   ;;

esac

echo $(date "+%Y/%m/%d %H:%M:%S") $deployment_selection $version $BUILD_ID $JENKINS_URL >> /var/jenkins_home/build.log