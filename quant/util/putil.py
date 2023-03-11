import asyncio
from threading import Thread
import psutil
import subprocess
import os

# 运行程序
from quant.util import fileutil

def asyn(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
@asyn
def run(file):
    if os.path.exists(file):
        rc,out= subprocess.getstatusoutput(file)

# 检测某程序是否已运行
def check_process(name):
    pl = psutil.pids()
    ret=0
    pname=""
    for pid in pl:
        if psutil.pid_exists(pid):
            try:
                pname=psutil.Process(pid).name()
            except:
                pass
        if pname == name:
            ret=pid
            # print(pid)
            break
    return ret

def check_run_gm():
    ret=0
    file = fileutil.get_config(section='GOLDMINER', key='path')
    fname=file.split('/')[-1]
    if check_process(fname)==0:
        run(file)
    else:
        ret=1
    return ret


if __name__=='__main__':
    check_run_gm()