# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:日志类
# Copyright (C) 2021-2023
###############################################################################
#
import datetime
import sys,os
base_dir=os.path.dirname(os.path.dirname(__file__))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
import logging
from quant.api.singleton import singleton

@singleton
class Logger():
    # 拙金数据API封装
    # quote_ctx = None
    def __init__(self):
        self.logger = logging.getLogger("mylogger")
        # StreamHandler对象自定义日志级别
        self.logger_leverl=logging.DEBUG
        self.logger.setLevel(self.logger_leverl)
        # 日志格式
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # info handler类型 ,0:stream,1:file,2:both
        self.handler_type=0


    # 获取流handler
    def get_stream_handler(self,level):
        stream_handler = logging.StreamHandler()
        # StreamHandler对象自定义日志格式
        stream_handler.setFormatter(self.formatter)
        stream_handler.setLevel(level)
        return stream_handler

    # 获取流handler
    def get_file_handler(self,type,level):
        log_file = "{}/log/{}_{}.txt".format(base_dir,type, datetime.datetime.now().strftime("%Y-%m-%d"))
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        return file_handler

    #     信息日志
    def loginfo(self,message):
        if self.handler_type==0:
            stream_handler=self.get_stream_handler(logging.INFO)
            self.logger.addHandler(stream_handler)
        elif self.handler_type==1:
            file_handler = self.get_file_handler('info',logging.INFO)
            self.logger.addHandler(file_handler)
        else:
            stream_handler = self.get_stream_handler(logging.INFO)
            self.logger.addHandler(stream_handler)

            file_handler = self.get_file_handler('info',logging.INFO)
            self.logger.addHandler(file_handler)

        self.logger.info(message)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

    #错误日志
    def logerror(self,message):
        handler = self.get_file_handler('error',logging.ERROR)
        self.logger.addHandler(handler)
        self.logger.error(message)
        self.logger.removeHandler(handler)

    # 调试日志
    def logdebug(self,message):
        handler = self.get_stream_handler(logging.DEBUG)
        self.logger.addHandler(handler)
        self.logger.debug(message)
        self.logger.removeHandler(handler)

if __name__=="__main__":
    Logger().loginfo("test done")
