import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
# loginfo(base_dir)
import configparser
import subprocess

def get_config(file=None,section=None,key=None):
    config = configparser.ConfigParser()
    if file==None:
        file='{}/{}'.format(base_dir,"config.ini")
    try:
        config.read(file,encoding=check_charset(file))
    except:
        config.read(file)
    return config[section][key]
def check_charset(file_path):
    import chardet
    with open(file_path, "rb") as f:
        data = f.read(4)
        charset = chardet.detect(data)['encoding']
    return charset

def set_config(file,section,key,value):
    # coding=utf-8
    cf = configparser.ConfigParser()
    try:
        cf.read(file,encoding=check_charset(file))
    except:
        cf.read(file)
    # cf.read(file)
    cf.set(section, key, value)
    cf.write(open(file, "w"))
    pass

def runfile(file):
    if os.path.exists(file):
        rc, out = subprocess.getstatusoutput(file)
    #     loginfo(rc)
    #     loginfo('*' * 10)
    #     loginfo(out)
    # pass

if __name__=='__main__':

    # file=get_config(section='GOLDMINER',key='path')
    # runfile(file)

    file=get_config(section='FUTU',key='path')
    runfile(file)
    # file="E:/temp/StockwayStock.ini"
    # loginfo(file)
    # str=get_config(file,'\SelfSelect','自选股')
    # # set_config("E:/temp/StockwayStock.ini", "\SelfSelect", "择时", "0.000333,0.002248,0.000905,1.600030,1.600050,")
    # loginfo(str)