# coding=utf-8
# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:盘后更新持仓数据到本地数据库
# Copyright (C) 2021-2023
###############################################################################
#
from __future__ import print_function, absolute_import

import datetime
import sys,os
import time

base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中

from quant.stockdata import StockData
from quant.brokers.myquantbroker import MyquantBroker
from quant.enums.brokers import Brokers
from quant.model.setting import Setting

from quant.util.configutil import get_config

from gm.api import *

# 盘后更新持仓数据到本地数据库
def init(context):
    # 订阅浦发银行, bar频率为一天和一分钟
    # 订阅订阅多个频率的数据，可多次调用subscribe
    # self.context = context
    # 获取当前setting帐号id
    if len(context.accounts) == 0:
        print("当然设置的帐号交易配置文件错误:略策文件没有挂接交易帐号")
        stop()

    #     获取交易帐号设置参数
    setting_account_id = Setting.get_setting_accountid(context)
    setting = Setting().getdata(setting_account_id)
    if setting == None:
        print(
            "当然设置的帐号：{}，交易配置文件错误：数据库setting表没有配置交易设置信息".format(context.setting_account_id))
        stop()
    else:
        context.setting = setting

    # context.backtest_id="{}{}".format(context.setting.account_id, context.backtest_id)
    # # 设置当然帐号对象
    # self.account = Account(self.context)
    #
    # # 显示输出交易帐号设置参数
    # self.account.display_run_param()

    # 设定经纪商
    # broker = get_borker(context=context, broker_type=setting.broker)
    # # 打印显示当前帐号资金信息
    # broker.display_account_asset_info()
    #
    # # 获取持仓信息并打印输出
    # positions = broker.getPositions(display=True)
    # print(positions)
    broker=get_borker(context,setting.broker)
    StockData.update_position(broker)
    # GmApi().update_execution_reports()
    # pos= Account(context).getPositions()
    # print(pos)
    print("-------------end update_position--------------------")
    print(datetime.datetime.now())
    time.sleep(30)
    stop()
    print("-------------stop--------------------")
    print(datetime.datetime.now())

#获取经纪商
def get_borker(context,broker_type):
    if broker_type==Brokers.xtquant.value:
        # broker=XtBroker(context=context)
        pass
    else:
        broker = MyquantBroker(context=context)
    return broker


def run_start():
    # check_run_gm()
    print("-------------start--------------------")
    print(datetime.datetime.now())
    # time.sleep(30)
    print(datetime.datetime.now())
    run_context()
    print("-------------end update_position--------------------")

def run_context():
    run(
        strategy_id=get_config('ACCOUNT','strategy_id'),
        # filename="{}\\quant\\{}".format(base_dir,'updateposition.py'),
        filename='updateposition.py',
        mode=MODE_LIVE,
        token=get_config('TOKEN','gmtoken'),
        # backtest_start_time='2020-11-01 08:00:00',
        # backtest_end_time='2020-11-10 16:00:00',
        # backtest_adjust=ADJUST_PREV,
        # backtest_initial_cash=10000000,
        # backtest_commission_ratio=0.0001,
        # backtest_slippage_ratio=0.0001
        )

if __name__ == '__main__':
    run_start()

