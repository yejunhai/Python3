# -*- coding: utf-8 -*-
# @Time : 2020-6-12 22:43
# @Author : yejunhai
# @Site : 
# @File : monitor.py
# @Software: PyCharm


import paramiko
import pymysql
import sys
import socket
import time
import requests
import json


def down_time(ip, table):
    cursor.execute(f"select {table}.start_time,{table}.end_time from {table} WHERE ip = '{ip}'")
    cpu_time = cursor.fetchone()
    try:
        start_time = cpu_time[0]
        end_time = cpu_time[1]
        duration = end_time - start_time
        return f"\n本次故障开始时间 {start_time}\n本次故障结束时间 {end_time}\n本次故障持续时间 {duration}"
    except:
        return "\n未记录故障时间"


class Check():

    def __init__(self, switch, threshold, client):
        self.switch = switch
        self.threshold = threshold
        self.client = client

    def cpu(self):
        if self.switch[1] == 1:
            stdin, stdout, stderr = self.client.exec_command(
                r"""iostat -x|awk NR==4'{printf(100-$6)}'""")
            cpu_result = stdout.read().decode()
            cursor.execute(f"select cpu.send from cpu WHERE ip = '{ip}'")
            send = cursor.fetchone()
            if cpu_result > str(self.threshold[1]) and send[0] == 0:
                cursor.execute(f"UPDATE cpu SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                print(f'{cur_time} {ip} {system_info} CPU使用率:{cpu_result}% 请检查')
            elif cpu_result < str(self.threshold[1]) and send[0] == 1:
                cursor.execute(f"UPDATE cpu SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                print(f'{cur_time} {ip} {system_info} CPU使用率:{cpu_result}% 已恢复!{down_time(ip, "cpu")}')
        return cpu_result

    def mem(self):
        if self.switch[2] == 1:
            stdin, stdout, stderr = self.client.exec_command(
                r"""free|awk '/Mem:/{printf("%.2f",($2-$4)/$2*100)}'""")
            mem_result = stdout.read().decode()
            stdin, stdout, stderr = self.client.exec_command(
                r"""free|awk '/Swap:/{if($2==0){printf$2}else{printf("%.2f",$3/$2*100)}}'""")
            swap_result = stdout.read().decode()
            cursor.execute(f"select mem.send from mem WHERE ip = '{ip}'")
            send = cursor.fetchone()
            if mem_result > str(self.threshold[2]) and send[0] == 0:
                cursor.execute(f"UPDATE mem SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                print(f'{cur_time} {ip} {system_info} 内存使用率:{mem_result}% swap使用率:{swap_result}% 请检查')
            elif mem_result < str(self.threshold[2]) and send[0] == 1:
                cursor.execute(f"UPDATE mem SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                print(
                    f'{cur_time} {ip} {system_info} 内存使用率:{mem_result}% swap使用率:{swap_result}% 已恢复{down_time(ip, "mem")}')
        return mem_result

    def disk(self):
        if self.switch[3] == 1:
            stdin, stdout, stderr = self.client.exec_command(
                r"""df -P|awk  -F "%" 'NR>1{print$1}'|awk '{print$1,$5}'|grep -v '/dev/sr0'""")
            disk_result = stdout.read().decode()
            cursor.execute(f"select disk.send from disk WHERE ip = '{ip}'")
            send = cursor.fetchone()
            disk_use_sum = []
            for disk in disk_result.split('\n'):
                disk = disk.split(' ')
                disk_name = disk[0]
                if disk_name == '':
                    break
                disk_use = disk[1]
                disk_use_sum.append(int(disk_use))
                if disk_use > str(self.threshold[3]) and send[0] == 0:
                    cursor.execute(f"UPDATE disk SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                    print(f'{cur_time} {ip} {system_info} 磁盘:{disk_name} 使用率:{disk_use}% 请检查')
            return sum(disk_use_sum)


db = pymysql.connect("127.0.0.1", user="root", passwd="root.123", db="monitor")
cursor = db.cursor()
# 数据表同步
cursor.execute("INSERT IGNORE INTO switch(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO threshold(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO cpu(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO mem(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO disk(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO speed(ip) SELECT info.ip FROM info")
cursor.execute("INSERT IGNORE INTO connect(ip) SELECT info.ip FROM info")
db.commit()

cursor.execute("select * from info")
info_table = cursor.fetchall()

for info_row in info_table:
    ip = info_row[0]
    system_info = info_row[1]
    phone = info_row[2]
    open = info_row[3]
    port = info_row[4]
    user = info_row[5]
    password = info_row[6]
    remote_port = info_row[7]
    if open != 1:
        continue
    try:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        client.connect(ip, port=remote_port, username=user,
                       password=password, timeout=3)

    except:
        print(f"{ip} 连接失败\n")
    cursor.execute(f"select * from switch where ip = '{ip}'")
    switch_row = cursor.fetchone()
    cursor.execute(f"select * from threshold where ip = '{ip}'")
    threshold_row = cursor.fetchone()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    check = Check(switch_row, threshold_row, client)
    check.cpu()
    check.mem()
    print(check.disk())

    db.commit()
    client.close()
db.commit()
db.close()
