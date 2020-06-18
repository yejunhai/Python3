# -*- coding: utf-8 -*-


import paramiko
import pymysql
import time
import requests
import json
import sys
#邮件告警
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def msg(text):
    #企业微信告警，wx表格控制，可以发送给不同的机器人，initiative控制是否@收件人，0关闭 1开启 默认关闭
    if wx != '':
        cursor.execute(f"select * from wx WHERE wx.name = '{wx}'")
        wx_row = cursor.fetchone()
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = wx_row[1]
        if wx_row[2] == 0:
            wx_phone = ''
        else:
            wx_phone = phone
        json_text = {
            "msgtype": "text",
            "text": {
                "content": text,
                "mentioned_mobile_list": [wx_phone]
            },
        }
        requests.post(api_url, json.dumps(json_text), headers=headers).content
    #邮件告警 需要配置好smtp发件代理，info表格填入邮件收件人，填入开启
    if mail != '':
        send_mail(text)


def send_mail(text):
    # 调用QQ第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "450433231@qq.com"  # 用户名
    mail_pass = ""  # 授权码 SMTP代理提供
    sender = '450433231@qq.com' #发件邮箱
    receivers = [f"{mail}"]  # 接收邮箱
    message = MIMEText(f'{text}', 'plain', 'utf-8')  # 正文
    message['From'] = Header("监控", 'utf-8')  # 发件人
    message['To'] = Header(f"{mail}", 'utf-8')  # 收件人
    subject = '【重要告警】'  # 主题
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
    except smtplib.SMTPException as f:
        out_log(f"{mail} 无法发送邮件", f)


def down_time(ip, table):
    #计算故障时间
    cursor.execute(f"select {table}.start_time,{table}.end_time from {table} WHERE ip = '{ip}'")
    cpu_time = cursor.fetchone()
    try:
        start_time = cpu_time[0]
        end_time = cpu_time[1]
        duration = end_time - start_time
        return f"\n开始时间 {start_time} 结束时间 {end_time} 持续时间 {duration}"
    except:
        return "\n未记录时间"


def out_log(text):
    #写日志
    with open(f'{sys.argv[0].split(".")[0]}.log', mode='a') as f:
        print(text, file=f)


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
            if float(cpu_result) > self.threshold[1] and send[0] == 0:
                cursor.execute(f"UPDATE cpu SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                msg(f'{cur_time} {ip} {system_info} CPU使用率:{cpu_result}% 请检查')
            elif float(cpu_result) < self.threshold[1] and send[0] == 1:
                cursor.execute(f"UPDATE cpu SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                msg(f'{cur_time} {ip} {system_info} CPU使用率:{cpu_result}% 已恢复{down_time(ip, "cpu")}')
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
            if float(mem_result) > self.threshold[2] and send[0] == 0:
                cursor.execute(f"UPDATE mem SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                msg(f'{cur_time} {ip} {system_info} 内存使用率:{mem_result}% swap使用率:{swap_result}% 请检查')
            elif float(mem_result) < self.threshold[2] and send[0] == 1:
                cursor.execute(f"UPDATE mem SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                msg(
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
                    msg(f'{cur_time} {ip} {system_info} 磁盘:{disk_name} 使用率:{disk_use}% 请检查')
            return sum(disk_use_sum)

    def speed(self):
        if self.switch[4] == 1:
            stdin, stdout, stderr = self.client.exec_command(
                r"""export LANG="en_US.UTF-8";sar -n DEV 1 1|grep "Average:"|grep "$(ifconfig |awk -F ":" '/flags/{print$1}'|egrep -v "lo|veth|docker")"|awk '{printf$5+$6}'""")
            speed_result = stdout.read().decode()
            cursor.execute(f"select speed.send from speed WHERE ip = '{ip}'")
            send = cursor.fetchone()
            if float(speed_result) > float(self.threshold[4]) and send[0] == 0:
                cursor.execute(f"UPDATE speed SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                msg(f'{cur_time} {ip} {system_info} 网卡速率:{speed_result}kB/s 请检查')
            elif float(speed_result) < float(self.threshold[4]) and send[0] == 1:
                cursor.execute(f"UPDATE speed SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                #msg(f'{cur_time} {ip} {system_info} 网卡速率:{speed_result}kB/s 已恢复{down_time(ip, "speed")}')
            return speed_result

    def connect(self):
        if self.switch[5] == 1 and port != None:
            stdin, stdout, stderr = self.client.exec_command(
                r"""ss -ant|grep "ESTAB"|grep "%s"|wc -l""" % port)
            connect_result = stdout.read().decode().replace("\n", "")
            stdin, stdout, stderr = self.client.exec_command(
                r"""ss -ant|wc -l""")
            connect_all_result = stdout.read().decode().replace("\n", "")
            cursor.execute(f"select connect.send from connect WHERE ip = '{ip}'")
            send = cursor.fetchone()
            if int(connect_result) > self.threshold[5] and send[0] == 0:
                cursor.execute(f"UPDATE connect SET send = 1,start_time = NOW() WHERE ip = '{ip}'")
                msg(
                    f'{cur_time} {ip} {system_info} ESTABLISHED并发连接数:{connect_result} 全状态连接数：{connect_all_result} 请检查')
            elif int(connect_result) < self.threshold[5] and send[0] == 1:
                cursor.execute(f"UPDATE connect SET send = 0,end_time = NOW() WHERE ip = '{ip}'")
                #msg(f'{cur_time} {ip} {system_info} ESTABLISHED并发连接数:{connect_result} 全状态连接数：{connect_all_result} 已恢复{down_time(ip, "connect")}')
            return connect_result, connect_all_result


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
# 获取需要监控的IP地址等信息
cursor.execute("select * from info")
info_table = cursor.fetchall()

for info_row in info_table:
    ip = info_row[0]
    system_info = info_row[1]
    phone = info_row[2]
    monitor = info_row[3]
    port = info_row[4]
    user = info_row[5]
    password = info_row[6]
    remote_port = info_row[7]
    mail = info_row[8]
    wx = info_row[9]
    # 是否开启监控 表格info.open控制，0关闭 1开启 默认开启
    if monitor != 1:
        continue
    try:
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        client.connect(ip, port=remote_port, username=user,
                       password=password, timeout=3)

    except:
        out_log(f"{ip} 连接失败\n")
    #表格switch控制监控项是否开启 0关闭 1开启 默认开启
    cursor.execute(f"select * from switch where ip = '{ip}'")
    switch_row = cursor.fetchone()
    #表格threshold设置不同的监控阈值 默认CPU 80 内存90 磁盘90 网卡60M 连接数800
    cursor.execute(f"select * from threshold where ip = '{ip}'")
    threshold_row = cursor.fetchone()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #开始登入巡检
    check = Check(switch_row, threshold_row, client)
    cpu_use = check.cpu()
    mem_use = check.mem()
    disk_all_use = check.disk()
    speed_use = check.speed()
    coonect_use = check.connect()
    client.close()
    db.commit()
    out_log(
        f"{cur_time} {ip} CPU使用率:{cpu_use}% 内存使用率:{mem_use}% 磁盘总0使用率:{disk_all_use}% 网卡速率:{speed_use}kB/s 端口{port} ESTABLISHED并发连接数{coonect_use[0]} 全状态连接数:{coonect_use[1]}")
db.commit()
db.close()
