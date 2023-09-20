#!/usr/bin/python3

import os
# import cgi, cgitb
import json

# cgitb.enable()
# form = cgi.FieldStorage()
# time = form.getvalue("time")
# os.system("sudo date -s "+"time")

# print("Content-type:text/html\n")

def get_cpu_info():
    cpu_temp = os.popen("vcgencmd measure_temp").readline().replace("temp=","").replace("'C\n","")
    cpu_freq = os.popen("vcgencmd get_config arm_freq").readline().replace("arm_freq=", "").replace("\n", "")
    cpu_use = float(os.popen("top -bn 1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())
    return (cpu_temp, cpu_freq, cpu_use)


def get_ram_info():
    ram_info = os.popen('free').readlines()[1].split()
    ram_total = int(ram_info[1])/1024
    ram_used = int(ram_info[2])/1024
    ram_free = int(ram_info[3])/1024
    ram_shared = int(ram_info[4])/1024
    ram_cache = int(ram_info[5])/1024
    return (ram_total, ram_used, ram_free, ram_shared, ram_cache)

def get_disk_info():
    disk_info = os.popen("df -h /").readlines()[1].split()
    disk_total = float(disk_info[1].replace("G", ""))
    disk_used = float(disk_info[2].replace("G", ""))
    disk_free = float(disk_info[3].replace("G", ""))
    return (disk_total, disk_used, disk_free)

def get_uptime():
    with open("/proc/uptime") as f:
        uptime = f.read().split()[0]
    return uptime

cpu_info = get_cpu_info()
ram_info = get_ram_info()
disk_info = get_disk_info()

init_val = {
    "uptime": get_uptime(),
    "time": os.popen("date '+%H:%M:%S'").readline(),
    "date": os.popen("date '+%Y-%m-%d'").readline(),
    "os": os.popen("uname -o").readline(),
    "mem":{"total": ram_info[0], "used": ram_info[1], "free": ram_info[2], "shared": ram_info[3], "cached": ram_info[4]},
    "disk": {"total": disk_info[0], "used": disk_info[1], "free": disk_info[2]},
    "cpu": {"temp": cpu_info[0], "freq": cpu_info[1], "use": cpu_info[2]}
}