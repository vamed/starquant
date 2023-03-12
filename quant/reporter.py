# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:盘后发送报告
# Copyright (C) 2021-2023
###############################################################################
#
import sys,os
base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
from quant.model.order import Order
from datetime import datetime
import pandas as pd
from quant.model.position import Position
from quant.model.setting import Setting

# 盘后发送报告
class Reporter():

    def __init__(self):
        pass

    def get_report(self,date=datetime.now().strftime('%Y-%m-%d')):

        df_acnt=Setting().get_trade_account(date=date)
        trade_html=""
        for i,row in df_acnt.iterrows():
            account_id= row['account_id']
            account_name= row['name']
            date= date
            df_dt=self.get_day_trade_record(account_id= row['account_id'],account_name= row['name'],date= date)
            if len(df_dt)>0:
                trade_html +="帐号：{}，帐号名称：{}，日期：{}，交易记录：<br>{}<br>".format(account_id, account_name,date,df_dt.to_html())

            trade_html +=self.get_position_report(account_id= row['account_id'],account_name= row['name'])

        htm="每天数据更新结果：<br><br>{}".format(trade_html)

        # 发送邮件
        # mailutil.send_mail(htm)
        print(htm)

    def get_day_trade_record(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',account_name='',date=datetime.now().strftime('%Y-%m-%d')):
        ret = Order().get_day_trade_record(account_id, date)
        return ret

    def get_day_trade_report(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',account_name='',date=datetime.now().strftime('%Y-%m-%d')):
        # 当天清仓盈利
        df_prof=Order().get_day_sellout_profit(account_id=account_id,date=date)
        if len(df_prof)==0:
            return ''
        df_profit=pd.DataFrame(data=df_prof.groupby("symbol").apply(lambda x:-(x['side']*x['price']*x['volume']).sum()),columns=['盈利'])
        # print(df_profit)
        # df_name=StockInfo().get_stock_by_symbols(df_profit.index.values)
        # df_profit['name']=df_name['name']
        df_profit['name']=''
        df_factor=Order().get_day_sellout_orders(date=date,account_id=account_id)

        if len(df_factor)>0:
            df_buy = Order().get_order_by_symbols(df_factor.index.values, account_id=account_id)
            df_buy=df_buy.loc[df_buy['side']==1,:]
            df_buy.sort_values(by='trade_time',ascending=False,inplace=True)
            df_buy.drop_duplicates(subset='symbol',keep='first',inplace=True)
            df_buy.set_index('symbol',inplace=True)

            df_profit['buy_strategy'] = df_buy['strategy']
            df_profit['buy_factor'] = df_buy['factor']
            df_profit['buy_date'] = df_buy['trade_date']
            df_profit['buy_price'] = df_buy['price']

            df_profit['sell_strategy'] = df_factor['strategy']
            df_profit['sell_factor'] = df_factor['factor']
            df_profit['sell_price'] = df_factor['price']
            df_profit['sell_date'] = df_factor['trade_date']

            htm_profit= df_profit.to_html()
            profit=round(df_profit['盈利'].sum(),2)

        else:
            htm_profit="当天没有清仓的交易"
            profit=0

        # df_picktime=Picker().get_live_picktime(export_eastmoney=True)
        account = "{}，ID:{}".format(account_name, account_id)

        ret="帐号：{}<br>每天清仓盈利(总计：{}元)：<br>{}<br>".format(account,profit,htm_profit)
        return ret

    def get_position_report(self,account_id,account_name):
        # 当天持仓明细
        ret=''
        df_pos=Position().get_local_position(account_id=account_id)
        if len(df_pos)==0:
            return ret
        df_pos=df_pos.loc[:,['symbol','name','volume','open_price','price','amount','market_value','profit_amount','profit_rate','date']]
        pos_profit=round(df_pos['profit_amount'].sum(),2)
        htm_pos=df_pos.to_html()
        account="{}，ID:{}".format(account_name,account_id)
        ret = "帐号：{}<br>每天持仓明细(持仓盈利总计：{}元)：<br>{}<br>".format(account,pos_profit,htm_pos)
        return ret
if __name__=="__main__":
    Reporter().get_report(date=datetime.now().strftime('%Y-%m-%d'))
    # Reporter().get_report(date='2023-01-10')