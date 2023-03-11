# coding=utf-8
# from __future__ import print_function, absolute_import
# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:实盘入口
# Copyright (C) 2021-2023
###############################################################################
#
import multiprocessing
import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中

import time
import argparse
import ctypes
import datetime
import inspect
from quant.logger import Logger
from quant.util.putil import check_run_gm
from gm.api import *
from quant.startengine import run_engine

# 强制杀死线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

#     停止线程
def stop_thread(thread):
    if thread.ident:
        _async_raise(thread.ident, SystemExit)

# 解析参数
def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Sample Skeleton'
        )
    )

    parser.add_argument('--mode', default='2',
                        required=False, help='mode运行模式, 实时模式:MODE_LIVE:1回测模式:MODE_BACKTEST:2')


    return parser.parse_args(pargs)

# 启动交易程序
def start_up(args=None):
    args = parse_args(args)
    Logger().logerror(args.mode)
    # run_strategy(args.mode)
    if args.mode=='2':
        check_run_gm()
        Logger().loginfo("-------------start--------------------")
        Logger().loginfo("-------------正在检测掘金客户端是否打开--------------------")
        time.sleep(30)
        stoped="stoped"
        running="running"
        status=stoped
        show_tip=True
        process_run_engine = multiprocessing.Process(target=run_engine,args=(args.mode,))
        while True:
            now=datetime.datetime.now()
            # 8：50和20：50掘金服务器暂停
            if (now.hour<8) or ((now.hour>8) and (now.hour<20)) or (now.hour>20):
                if status!=running:
                    Logger().loginfo(datetime.datetime.now())
                    process_run_engine = multiprocessing.Process(target=run_engine,args=(args.mode,))
                    Logger().loginfo("-------------策略正在初始化-------------")
                    process_run_engine.start()
                    status=running
                    Logger().loginfo("-------------策略正在运行-------------")
            elif (now.hour==8) or ((now.hour==20)):
                if show_tip:
                    Logger().loginfo("-------------当前时间服务有问题，回测程序停止-----------------")
                    show_tip=False
                # if status!=stoped:
                else:
                    # stop()
                    stop_thread(process_run_engine)
                    status=stoped
                    Logger().loginfo("-------------策略已停止-------------")
                    for i in range(10):
                        print(i)
                        time.sleep(1)
                    sys.exit()
            time.sleep(1)

    elif args.mode == '3':
        run_engine('3')

    else:
        process_run_engine = multiprocessing.Process(target=run_engine,args=(args.mode,))
        check_run_gm()
        Logger().loginfo("-------------start--------------------")
        Logger().loginfo("-------------正在检测掘金客户端是否打开--------------------")
        time.sleep(30)
        stoped="stoped"
        running="running"
        status=stoped
        show_tip=True

        while True:
            now=datetime.datetime.now()
            if (now.hour>=9) and  (now.hour<16):
                if status!=running:
                    Logger().loginfo(datetime.datetime.now())
                    process_run_engine = multiprocessing.Process(target=run_engine,args=(args.mode,))
                    Logger().loginfo("-------------策略正在初始化-------------")
                    process_run_engine.start()
                    status=running
                    Logger().loginfo("-------------策略正在运行-------------")
            else:
                if show_tip:
                    Logger().loginfo("-------------当前非交易时间，交易程序停止-----------------")
                    show_tip=False
                if status!=stoped:
                    # stop()
                    stop_thread(process_run_engine)
                    status=stoped
                    Logger().loginfo("-------------策略已停止-------------")
                    for i in range(10):
                        print(i)
                        time.sleep(1)
                    sys.exit()
            time.sleep(1)

if __name__ == '__main__':

    # start_up(["--mode=3"])
    # start_up(["--mode=2"])
    start_up(["--mode=1"])
    # start_up()

