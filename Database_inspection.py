#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paramiko
import sys


def ssh_connect(host, username, password, commands):
    # 连接到目标主机
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username,
                       password=password, timeout=1)
        # 执行命令
        for command in commands:
            print(command + ' result:')
            stdin, stdout, stderr = client.exec_command(
                ". ./.bash_profile;" + command, timeout=3)
            print(stdout.read().decode() + stderr.read().decode())
        return 0
    except:
        print('Connection failed')
        return 1


def main():
    #判断传参
    if len(sys.argv[:]) < 5:
        print(
            """fail parameter error\nEXAMPLES:python3 %s "host" "username" "password" "command1;command2" """ % sys.argv[0])
        sys.exit(1)
    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    commands = str(sys.argv[4]).split(';')
    return ssh_connect(host, username, password, commands)


if __name__ == '__main__':
    result = main()
    sys.exit(result)