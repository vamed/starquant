import configparser
import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
# loginfo(base_dir)
def get_config(section,key):
    config = configparser.ConfigParser()
    # loginfo('{}/{}'.format(base_dir,"config.ini"))
    config.read('{}/{}'.format(base_dir,"config.ini"))
    return config[section][key]

def set_config(file,section,key,value):
    # coding=utf-8
    import sys
    cf = configparser.ConfigParser()
    cf.read(file)
    cf.set(section, key, value)
    cf.write(open(file, "w"))
    pass
if __name__=='__main__':
    # str=get_config('TOKEN','gmtoken')
    set_config("E:/temp/StockwayStock.ini", "\SelfSelect", "择时", "0.000333,0.002248,0.000905,1.600030,1.600050,")
    # loginfo(str)