# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:
# Copyright (C) 2021-2023
###############################################################################
#
import datetime
import numpy as np
import pandas as pd

from quant.api.gmapi import GmApi
from quant.api.tdxapi import TdxApi
from quant.brokers.myquantbroker import MyquantBroker
from quant.enums.brokers import Brokers
from quant.enums.ratings import Ratings
from quant.indicators import Indicator
from quant.model.order import Order
from quant.model.stockpool import StockPool
from quant.model.position import Position
from quant.util import stockutil

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)

class StockData():
    #
    def __init__(self):
        pass

    #获取区间日数据，并更新kdj
    @classmethod
    # def update_indicator(self,symbols,date):
    def update_indicator(self,acount_id, buy_symbols,positions, date):
        start = (date + datetime.timedelta(days=-200)).strftime("%Y-%m-%d")
        # start = stockutil.get_date_pren_trade(20)
        end = (date + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        holding_symbols =[]
        if len(positions)>0:
            df_pos = Position.to_df(positions)
            df_pos.set_index('symbol',inplace=True)
            holding_symbols=df_pos.index.values
        # symbols=buy_symbols+holding_symbols
        symbols=np.hstack((buy_symbols, holding_symbols))
        df = GmApi().getHistoryData(list(symbols), start, end)
        df_sym= df['symbol'].value_counts()

        for s in df_sym[df_sym<20].index:
            df.drop(df[df['symbol']==s].index,axis=0,inplace = True)
            df_s = GmApi().getHistoryNKdata(s, count=30, end_date=end)
            df=pd.concat([df,df_s],axis=0,ignore_index=True)

        df_stock=df.sort_values(by='eob',ascending=False).copy()

        df_stock.drop_duplicates(subset=['symbol'], keep='first', inplace=True)
        # df['strategy']=''
        # df['open_price']=0
        # df['stock_type']=''
        # 获取股票停牌信息
        # df_stock['suspension'] = False
        # df_stock.loc[df_stock['date']<end,['suspension']]=True

        df_buy_symbols=StockPool().get_symbols_strategy(buy_symbols)
        df_holding_symbols = Position().get_symbols_strategy(account_id=acount_id,symbols=holding_symbols)
        if len(positions) > 0:
            df_holding_symbols['open_price']=df_pos['open_price']
        df_strategy = pd.concat([df_buy_symbols, df_holding_symbols.loc[~df_holding_symbols.index.isin(df_buy_symbols.index),:]],axis=0)

        df_strategy['strategy'].fillna(value='',inplace=True)
        df_strategy['open_price'].fillna(value=0, inplace=True)
        df_strategy['stock_type'].fillna(value='', inplace=True)

        for index, row in df_stock.iterrows():
            # 如果当前股票停牌，不计算指标
            # if row['suspension']==True:
            #     continue

            df_indicator = df.loc[df['symbol'] == row['symbol'], :]

            df_indicator = Indicator.kdj(df_indicator)
            # df_indicator = Indicator.mtm(df_indicator)
            # df_indicator = Indicator.atr(df_indicator)
            # df_indicator = Indicator.boll(df_indicator)
            # df_indicator = Indicator.macd(df_indicator)
            # df_indicator = Indicator.sma(df_indicator)
            # df_indicator=Technical().cal_minuteline(df_indicator)

            # print("-------------------boll指标----------------")
            # boll指标
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_boll_low'] = df_indicator.boll_low.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_boll_up'] = df_indicator.boll_up.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_boll_mid'] = df_indicator.boll_mid.values[-1]
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_close'] = df_indicator.close.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_close_array'] =str(df_indicator.close[-26:].values)

            # kdj相关指示
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'high'] = df_indicator.iloc[-8:, :].high.max()
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'low'] = df_indicator.iloc[-8:, :].low.min()

            if len(df_indicator.k)<2:
                print(row['symbol'])
            #     kdj
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'k_pre'] = df_indicator.k.values[-1]
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'd_pre'] = df_indicator.d.values[-1]
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'j_pre'] = df_indicator.j.values[-1]

            # atr
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'tr'] = df_indicator.tr.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'atr'] = df_indicator.atr.values[-1]

            # mtm
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_mtm'] = df_indicator.mtm.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_mtmma'] = df_indicator.mtmma.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pren_close'] = df_indicator.close.values[-12]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'mtm5'] =np.round( np.sum(df_indicator.mtm[-5:].values),3)
            #
            # # macd
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_short_ema'] = df_indicator.short_ema.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_long_ema'] = df_indicator.long_ema.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_dea'] = df_indicator.dea.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_dif'] = df_indicator.dif.values[-1]

            # sma
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_ma5'] = df_indicator.ma5.values[-1]
            # df_stock.loc[df_stock['symbol'] == row['symbol'], 'pre_ma10'] = df_indicator.ma10.values[-1]

            df_stock.loc[df_stock['symbol'] == row['symbol'], 'date'] = date.strftime("%Y-%m-%d")

            df_stock.loc[df_stock['symbol'] == row['symbol'], 'strategy']=''
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'stock_type'] = ''
            df_stock.loc[df_stock['symbol'] == row['symbol'], 'open_price'] = 0
            if len(df_strategy)>0:
                if row['symbol'] in df_strategy.index.values:
                    df_stock.loc[df_stock['symbol'] == row['symbol'], 'strategy'] = df_strategy.at[row['symbol'],'strategy']
                    df_stock.loc[df_stock['symbol'] == row['symbol'], 'open_price'] = df_strategy.at[row['symbol'], 'open_price']
                    df_stock.loc[df_stock['symbol'] == row['symbol'], 'stock_type'] =df_strategy.at[row['symbol'], 'stock_type']

        # 重置资金流数据
        df_stock['inflow']=0
        df_stock['inflow_time']=datetime.datetime.strptime("{} {}".format(datetime.datetime.now().strftime("%Y-%m-%d"),"09:30:00"),"%Y-%m-%d %H:%M:%S")
        # df['strategy'].fillna(value='',inplace=True)
        # df['open_price'].fillna(value=0, inplace=True)
        # df['stock_type'].fillna(value='', inplace=True)
        return df_stock

    # 获取某股票主力资金流
    def get_main_money_flow(self,code):
        df=TdxApi().get_transaction_data(code)
        # print(df)
        return df

    # 获取经纪商
    def get_borker(context, broker_type):
        if broker_type == Brokers.xtquant.value:
            # broker = XtBroker(context=context)
            pass
        else:
            broker = MyquantBroker(context=context)
        return broker

    # 获取当前持仓明细
    @classmethod
    def update_position(self,broker):
        # 设定经纪商
        # broker = self.get_borker(context=context, broker_type=broker_type)
        # # 打印显示当前帐号资金信息
        # broker.display_account_asset_info()

        # 获取持仓信息并打印输出
        pos = broker.getPositions(display=True)
        account_id=''
        if len(pos) > 0:
            df_pos = Position.to_df(pos)
            df_pos['update_time'].fillna(value=broker.context.now, inplace=True)
            df_pos['created_at'].fillna(value=broker.context.now, inplace=True)
            df_pos['code'] = df_pos['symbol'].apply(lambda x: stockutil.delSymbolPrefix(x))
            df_pos.set_index('code', inplace=True, drop=True)
            df_pos['factor_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            df_pos['date'] = datetime.datetime.now().strftime("%Y-%m-%d")

            # df_ent = Picker().update_stock_pool_entend_info(df_pos.copy())
            df_close = GmApi().get_current_close(df_pos['symbol'].values)

            df_close['code'] = df_close['symbol'].apply(lambda x: stockutil.delSymbolPrefix(x))
            df_close.set_index('code', inplace=True)

            # df_ent['symbol'] = df_pos['symbol']
            # df_ent['update_time'] = df_pos['update_time']
            # df_ent['created_at'] = df_pos['created_at']

            df_pos['price'] = df_close['close']
            # df_ent['symbol'] = df_pos['symbol']

            # df_ent['yesterday_volume'] = df_pos['yesterday_volume']
            df_pos['factor'] = ''
            df_pos['rating'] = Ratings.Holding.value
            df_pos['strategy'] = ''
            # df_ent['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            # df_ent['seldate'] = datetime.datetime.now().strftime("%Y-%m-%d")
            # df_ent['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_pos = df_pos.loc[:,
                     ['account_id', 'symbol', 'name', 'open_price', 'volume', 'amount', 'can_use_volume',
                      'frozen_volume', 'on_road_volume', 'price', 'market_value', 'profit_amount', 'profit_rate',
                      'factor', 'rating', 'strategy',
                      'date', 'update_time', 'created_at']]

            account_id = df_pos['account_id'].values[0]
            if len(df_pos) > 0:
                df_order = Order().get_order_by_symbols(df_pos['symbol'].values, account_id=account_id)
                for i, row_pos in df_pos.iterrows():
                    for j, row_order in df_order.iterrows():
                        if row_pos['symbol'] == row_order['symbol']:
                            if row_pos['created_at'].strftime("%Y-%m-%d") == row_order['trade_date']:
                                df_pos.at[i, 'strategy'] = row_order['strategy']
                                break

                # 更新持仓中策略设置
                df_pos_local = Position().get_local_position(account_id=account_id)
                for i, row_pos in df_pos.iterrows():
                    for j, row_pos_local in df_pos_local.iterrows():
                        if row_pos['symbol'] == row_pos_local['symbol']:
                            df_pos.at[i, 'strategy'] = row_pos_local['strategy']
                            if row_pos_local['rating']!='':
                                df_pos.at[i, 'rating'] = row_pos_local['rating']
                            break
            Position().delete_all(account_id=account_id)
            Position().batch_insert(df_pos)
            # return df
        else:
            Position().delete_all(account_id=account_id)

    # 超大单：大于等于50万股或者100万元的委托单；
    # 大单：大于等于10万股或者20万元且小于50万股和100万元的委托单；
    # 中单：大于等于2万股或者4万元且小于10万股和20万元的委托单；
    # 小单：小于2万股和4万元的委托单；
    # 流入：买入成交额；
    # 流出：卖出成交额；
    # 主力流入：超大单加大单买入成交额之和；
    # 主力流出：超大单加大单卖出成交额之和；
    # 主力净流入：主力流入-主力流出；
    # 净额：流入-流出；净占比:：（流入-流出）/总成交额
    def get_instant_inflow(self,code = '300308'):
        super_amount=1000000
        big_amount = 200000
        middle_amount = 40000
        # little_amount = 40000
        df = self.get_main_money_flow(code)
        df['vol']=df['vol']*100
        df['amount'] = df['amount'] * 100
        # df['mean_amount']=df['amount']/df['amount']
        df.dropna(axis=0, how='all', inplace=True)
        df['buyorsell'] = df['buyorsell'].astype(int)
        #

        df['super'] = 0
        df['big'] = 0
        df['middle'] = 0
        df['little'] = 0
        df['super'] = df.apply(lambda x: x['amount'] if (x['amount'] >=super_amount ) else 0, axis=1)
        df['big'] = df.apply(lambda x: x['amount'] if ((x['amount'] < super_amount) and (x['amount'] >= big_amount)) else 0, axis=1)
        df['middle'] = df.apply(lambda x: x['amount'] if ((x['amount'] >= middle_amount) and (x['amount'] < big_amount)) else 0, axis=1)
        df['little'] = df.apply(lambda x: x['amount'] if (x['amount'] < middle_amount) else 0, axis=1)
        # df['super']=df.apply(lambda x:x['vol'] if (x['vol']>=5000) else 0 ,axis=1)
        # df['big']=df.apply(lambda x:x['vol'] if ((x['vol']<5000) and (x['vol']>=1000)) else 0 ,axis=1)
        # df['middle']=df.apply(lambda x:x['vol'] if ((x['vol']>=200) and (x['vol']<1000)) else 0 ,axis=1)
        # df['little']=df.apply(lambda x:x['vol'] if (x['vol']<200) else 0 ,axis=1)
        df['buyorsell'] = df.apply(lambda x: 1 if (x['buyorsell'] == 0) else -1 if (x['buyorsell'] == 1) else 0, axis=1)
        # df['super'] = (df['super'] * df['buyorsell']).cumsum()
        # df['big'] = (df['big'] * df['buyorsell']).cumsum()
        # df['middle'] = (df['middle'] * df['buyorsell']).cumsum()
        # df['little'] = (df['little'] * df['buyorsell']).cumsum()

        df['super'] = df['super'] * df['buyorsell']
        df['big'] = df['big'] * df['buyorsell']
        df['middle'] = df['middle'] * df['buyorsell']
        df['little'] = df['little'] * df['buyorsell']
        print(df)
        df.to_csv("e:\\{}-tx.csv".format(code))

        df_grp = df.groupby(by=['time']).agg(
            {'super': np.sum, 'big': np.sum, 'middle': np.sum, 'little': np.sum}
        )

        df_grp['super_cum'] = df_grp['super'].cumsum()
        df_grp['big_cum'] = df_grp['big'].cumsum()
        df_grp['middle_cum'] = df_grp['middle'].cumsum()
        df_grp['little_cum'] = df_grp['little'].cumsum()
        df_grp['inflow']=df_grp['super_cum']+df_grp['big_cum']+df_grp['middle_cum']+df_grp['little_cum']
        df_grp.to_csv("e:\\{}-tx_sum.csv".format(code))
        # print(df_grp)
        ret=df_grp.loc[:,['inflow','little_cum','middle_cum','big_cum','super_cum']].copy()
        ret.rename(columns={'super_cum':'super','big_cum':'big','middle_cum':'middle','little_cum':'little'},inplace=True)
        print(ret)

        return ret

if __name__=="__main__":

    code='SHSE.000001'
    df=StockData().get_instant_inflow(code=code)

    print(df)

