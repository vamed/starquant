import math
import numpy as np

def get_ticks(max,n):
    pos=0
    if max<0:
        pos=-1
        max=abs(max)
    step = max / n
    st_n = int(math.log10(step))
    if st_n>0:
        step = round((step / math.pow(10, st_n)), 0) * math.pow(10, st_n)
    else:
        step =round(round((step / math.pow(10, st_n)),1) * math.pow(10, st_n),1-st_n)
    end=step*n
    if (max>end):
        n=n+1
        end=step*n
    if pos==0:
        end = end + step
        ret=np.arange(0,end,step)
    else:
        ret=np.arange(-end,0,step)
    return ret


def get_step(max):
    max_m=math.log10(max)
    st=max/2
    st_n=int(math.log10(st))
    st=int(st/math.pow(10, st_n))*10
    # st=math.pow(10, zero_m-1)*5

    return st

# 浮点数转换
def parse_float(number):
    ret=number
    if number!=None:
        if np.isnan(number):
            ret=None
    return ret

#取整百
def get_neat(i):
    ret=0

    if i<100:
        ret=0
    else:
        p=pow(10,len(str(i))-1)
        ret=int(i/p)*p
    return ret

#取整百
def get_n_number(d,i):
    ret=d
    if d>pow(10,i+1):
        log=np.log10(d)
        ret=d/pow(10,int(int(log)))*pow(10,i)
    return int(ret)

if __name__=="__main__":
    # print(get_neat(239487))
    # d=len(search("\.(0*)", "5.00060030").group(1))
    # dist = int(math.log10(abs(0.000060030)))
    # s= get_ticks(100,2)
    # s2 = get_ticks(-0.03, 2)
    # s1 = get_ticks(-110,2)
    # # s = get_ticks(310, 2)
    #
    # s3 = get_ticks(0.15,2)
    # s4 = get_ticks(0.0006,4)
    # s5 = get_ticks(6,3)
    # s5 = get_ticks(4,2)
    # s5 = get_ticks(9,2)
    # s5 = get_ticks(20,2)
    # s5 = get_ticks(60,2)

    # p= np.log10(23000)
    # print(p)
    # print(int(p))
    #
    # p10=pow(10,int(p))
    # print(p10)
    p=get_n_number(999999,4)
    print(p)
    pass
    # findzero(0.004)
