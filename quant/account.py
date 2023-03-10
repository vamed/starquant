# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:帐号类
# Copyright (C) 2021-2023
###############################################################################
#
from gm.enum import MODE_BACKTEST
from quant.metric import Metric

class Account():
    # 初始化交易参数
    def __init__(self,context):
        # 最大仓位
        self.MAX_POSITION=context.setting.max_position
        # 单股最大创位
        self.MAX_SINGLE_POSITION = context.setting.max_single_position
        # 最大持股数
        self.MAX_STOCK_NUMBER=context.setting.max_stock_number
        # 单股单次购买金额
        self.PER_BUY_AMOUNT=context.setting.per_buy_amount
        # 经纪商myquant,xtquant
        self.broker = context.setting.broker
        # 帐号ID
        self.account_id = context.setting.account_id
        # 帐号名称
        self.name=context.setting.name
        # 帐号类型
        self.account_type=context.setting.account_type
        # 初始总资金
        self.initial_capital = context.setting.initial_capital
        # #
        self.context=context
        #
    #     获取帐号ID
    def get_account_id(self):
        ret=self.account_id
        if self.context.mode==MODE_BACKTEST:
            if self.context.backtest_account_id=="":
                ret="{}{}".format(self.context.setting.account_id, self.context.backtest_id)
            else:
                ret=self.context.backtest_account_id
        return ret

    #打印显示当前帐号交易设置信息
    def display_run_param(self):
        print("=========================交易设置参数信息===============================")
        func_Account_type=lambda x:"实盘帐号" if x==1 else "测试帐号"
        print("当前运行帐号：{},id:{},帐号类型:{}".format(self.name,self.account_id,func_Account_type(self.account_type)))
        print("最大持仓位：{:.2f}%".format(self.MAX_POSITION*100))
        print("最大持股数：{}".format(self.MAX_STOCK_NUMBER))
        print("单股单次购买金额：{}".format(self.PER_BUY_AMOUNT))
        print("最大单股持仓位：{:.2f}%".format(self.MAX_SINGLE_POSITION*100))

    # 更新最大仓位设置
    def update_position_setting(self):
        win_rate= Metric().get_win_rate(account_id=self.get_account_id())
        pos=self.get_kelly_position(win_rate[0],win_rate[1],win_rate[2])
        # 更新最大仓位设置
        self.MAX_POSITION=pos
        # 最大持股数
        # 单股单次购买金额
        if self.PER_BUY_AMOUNT<(self.MAX_POSITION/self.MAX_STOCK_NUMBER)*self.initial_capital:
            self.PER_BUY_AMOUNT= (self.MAX_POSITION/self.MAX_STOCK_NUMBER)*self.initial_capital
    # 凯利公式计算最大仓位
    @classmethod
    def get_kelly_position(self,win_rate,exp_win,exp_loss):
        ret=0.1
        if (win_rate>0) and (exp_win>0):
            ret=win_rate-((1-win_rate)/exp_win*abs(exp_loss))
        if ret<0:
            ret=0
        return ret


if __name__=="__main__":
    pos=Account.get_kelly_position(0.21,0.0363,-0.0032)
    print(pos)
