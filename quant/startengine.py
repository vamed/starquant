# coding=utf-8
# from __future__ import print_function, absolute_import
# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:入口
# Copyright (C) 2021-2023
###############################################################################
#
import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中

import datetime
from quant.logger import Logger
from quant.util.configutil import get_config
from gm.api import *
from quant.quantengine import QuantEngine
from quant.model.backtestrecord import BacktestRecord
from quant.util import globalvars

# 回测帐号ID

# 策略中必须有init方法
def init(context):
    subscribe(symbols='SHSE.000001', frequency='60s', count=1)
    # subscribe(symbols='SHSE.600030,SHSE.600050,SHSE.600007', frequency='60s', count=200)
    # 设置回测模式帐号ID
    print(globalvars.hand_trade)
    if (context.mode==MODE_BACKTEST):
        context.backtest_id=globalvars.backtest_id
        context.backtest_account_id=''
        if globalvars.backtest_account_id!='':
            context.backtest_account_id = globalvars.backtest_account_id

    context.quantengine=QuantEngine(context)

def on_bar(context, bars):
    # print(bars)
    context.quantengine.on_bar(context,bars)

def on_tick(context, tick):
    # print(tick)
    # logdebug(tick)
    context.quantengine.on_tick(context,tick)

# 响应委托状态更新事情，下单后及委托状态更新时被触发。
def on_order_status(context, order):
    context.quantengine.on_order_status(context, order)

# 响应委托被执行事件，委托成交或者撤单拒绝后被触发。
def on_execution_report(context, execrpt):
    context.quantengine.on_execution_report(context, execrpt)

# 响应交易账户状态更新事件，交易账户状态变化时被触发。
def on_account_status(context, account):
    # Logger().logdebug(account)
    pass

#当发生异常情况，比如断网时、终端服务崩溃是会触发
def on_error(context, code, info):
    # print(context.now)
    # Logger().loginfo(code)
    Logger().logerror(info)

# 在回测模式下，回测结束后会触发该事件，并返回回测得到的绩效指标对象
def on_backtest_finished(context, indicator):
    BacktestRecord().update_backtest_record(account_id=context.backtest_account_id,date=context.now.strftime("%Y-%m-%d %H:%M:%S"), status="finished")
    Logger().loginfo(indicator)

def run_engine(mode):
    # globalvars.hand_trade=ht
    if mode=='1':
        strategy_id = get_config('ACCOUNT', 'strategy_id')
        run_mode=MODE_LIVE
        Logger().loginfo("mode运行模式, 实时模式:MODE_LIVE:1")
    else:
        strategy_id = get_config('ACCOUNT', 'backtest_strategy_id')
        run_mode = MODE_BACKTEST
        Logger().loginfo("mode运行模式, 回测模式:MODE_BACKTEST:2")

    # backtest_start_time = '2022-03-03 08:00:00'
    backtest_start_time = '2022-05-27 08:00:00'
    backtest_end_time = '2023-02-27 16:00:00'
    # backtest_end_time =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if run_mode==MODE_BACKTEST and mode=='2':
        br=BacktestRecord().get_suspend_record()
        if br== None:
            # 回测模式帐号ID
            globalvars.backtest_account_id = "{}{}".format("back_test", globalvars.backtest_id)
            br=BacktestRecord()
            br.account_id=globalvars.backtest_account_id
            br.start=backtest_start_time
            br.current = backtest_start_time
            br.end = backtest_end_time
            br.date=datetime.datetime.now().strftime("%Y-%m-%d")
            br.status="start"
            br.symbols=""
            br.insert()
        else:
            globalvars.backtest_account_id=br.account_id
            backtest_start_time=br.current
        # pass
    try:
        run(strategy_id=strategy_id,
            filename='startengine.py',
            mode=run_mode,
            token=get_config('TOKEN','gmtoken'),
            backtest_start_time=backtest_start_time,
            backtest_end_time=backtest_end_time,
            backtest_adjust=ADJUST_PREV,
            backtest_initial_cash=1000000,
            backtest_commission_ratio=0.0001,
            backtest_slippage_ratio=0.0001)
    except Exception as e:
        Logger().loginfo(e)
        Logger().logerror(e)


# if __name__ == '__main__':
#
#     # start_up(["--mode=3"])
#     # start_up(["--mode=2","--ht=1"])
#     # run_engine(["--mode=1"])
#     # start_up()
#     pass

