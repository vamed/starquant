import os
import sys

base_dir=os.path.dirname(os.path.dirname(__file__))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
# 时间比较  格式hh:mm
import datetime

# 日期大小比较
def time_compare(time1,timestr):
    ret=False
    t1=float(time_compare(get_time_string(time1).replace(':','.')))
    t2 = float(timestr.replace(':', '.'))
    if t1>=t2 :
        ret=True
    return ret
# 格式化日期输出时间部分'%H:%M'
def get_time_string(date):
    return date.strftime('%H:%M')

# 计算交易时间过去的分钟数
def get_pass_minutes(date):
    hour=date.hour
    minute=date.minute
    ret=0
    if hour<9:
        ret=0
    elif hour>=15:
        ret=240
    elif hour >=9 and hour<12:
        ret = (hour-9)*60+minute-30
    elif hour == 12:
        ret = 120
    elif hour >12 and hour<15:
        ret = (hour-11)*60+minute
    return ret-1
    pass

def add_minutes(stime,mins):
    time= stime.split(':')
    hour= int(time[0])
    minute=int(time[1])
    minute=minute + mins
    if minute>=60:
        minute=minute%60
        hour=hour+1
        if hour>=24:
            hour=hour%24
    return "{}:{}".format(str(hour).rjust(2, '0'),str(minute).rjust(2, '0'))

def count_differ_days(time_a, time_b):
    """
    计算日期相差天数
    """
    # 因为得到的是UTC时间，所以需要UTC时间+8
    time_a = time_a + datetime.timedelta(hours=8)
    time_b = time_b + datetime.timedelta(hours=8)

    d1 = datetime.date(time_a.year, time_a.month, time_a.day)
    d2 = datetime.date(time_b.year, time_b.month, time_b.day)

    return (d1 - d2).days

if __name__=='__main__':
    print(add_minutes("23:55",5))