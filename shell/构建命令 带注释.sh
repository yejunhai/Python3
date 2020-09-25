#bin/bash

set -e -u

export LANG=en_US.UTF-8
#指定Gradle版本
export PATH=$PATH:/var/jenkins_home/tools/hudson.plugins.gradle.GradleInstallation/Gracle_5.6.1/bin/
#进入项目构建指定目录
build_dir=/var/jenkins_home/workspace/sdk-api/api
#构建后的备份目录，第一次构建后会生成
back_dir=/var/jenkins_home/jobs/sdk-api/builds/$version/archive/api/build/libs
#构建命令
build_command='gradle shadowJarAliYunRelease'
#定义更新的主机组 ansible需要调用
hosts=sdk-api
#远端服务器jar包存放位置
jarpath=/root/local/apps/sdk-api
#指定主机清单
inventory=/inventory/$hosts.yaml

#登入目标主机更新应用
update(){
	ansible $hosts[$1] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb_vs.py stop"
	ansible $hosts[$1] -i $inventory -m script -a "/sh/user_check.sh"
	ansible $hosts[$1] -i $inventory -m copy -a "src=$build_dir/build/libs/ dest=$jarpath/"
	ansible $hosts[$1] -i $inventory -m shell -a "cd $jarpath;sh server.sh stop"
	ansible $hosts[$1] -i $inventory -m shell -a "cd $jarpath;sh server.sh start"
	ansible $hosts[$1] -i $inventory -m script -a "/sh/http_status.sh"
	sleep 5
}

move(){
	if [ $version -eq 0 ];then
		echo "Version not specified"
		exit 1
	fi
	rm -rf $build_dir/build/libs
	cp -rp $back_dir $build_dir/build/
	cd $build_dir/build/libs && ls || exit 1
}

all_update(){
	host_number=$(grep -v "^\[" $inventory |wc -l)
	for ((i=0;i<$host_number;i++))
	do
		update $i
		ansible $hosts[$i] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb_vs.py start"
	done
}

case $deployment in

only_build)
	echo "begin $deployment "
	cd  $build_dir
	$build_command
	exit 0
	;;

deploy)
	echo "begin $deployment "
	cd  $build_dir
	$build_command
	update 0
	exit 0
	;;

rollback)
	echo "begin $deployment  version=$version"
	move
	update 0
	ansible $hosts[0] -i $inventory -m shell -a "cd /data/py;python3 aliyun_slb_vs.py start"
	exit 0
	;;

all_deploy)
	echo "begin $deployment"
	cd  $build_dir
	$build_command
	all_update
	exit 0
	;;

all_rollback)
	echo "begin $deployment  version=$version"
	move
	all_update
	exit 0
	;;

   *)
    exit 1
   ;;

esac

echo $(date "+%Y/%m/%d %H:%M:%S") $deployment $version $BUILD_ID $JENKINS_URL >> /var/jenkins_home/build.log