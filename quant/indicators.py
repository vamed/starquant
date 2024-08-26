# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:指标类
# Copyright (C) 2021-2023
###############################################################################
#

import numpy as np
import talib
import pandas as pd
from quant.api.gmapi import GmApi

class Indicator():
    def __init__(self):
        pass
    # sma
    @classmethod
    def sma(self,df):
        df.loc[:, 'ma5'] = talib.MA(df.close, timeperiod=5, matype=0)
        df.loc[:, 'ma10'] = talib.MA(df.close, timeperiod=10, matype=0)
        df.loc[:, 'ma20'] = talib.MA(df.close, timeperiod=20, matype=0)
        df.loc[:, 'ma60'] = talib.MA(df.close, timeperiod=60, matype=0)
        df.loc[:, 'ma120'] = talib.MA(df.close, timeperiod=120, matype=0)
        df.loc[:, 'ma250'] = talib.MA(df.close, timeperiod=250, matype=0)
        return df

    # macd
    @classmethod
    def macd(self,df):
        adjust=True
        df['dif'] = df['close'].ewm(span=12, adjust=adjust).mean() - df['close'].ewm(span=26, adjust=adjust).mean()
        df['dea'] = df['dif'].ewm(span=9, adjust=adjust).mean()
        df['macd'] = 2 * (df['dif'] - df['dea'])
        df['short_ema']=np.round(talib.EMA(df['close'].values, 12),3)
        df['long_ema'] = np.round(talib.EMA(df['close'].values, 26), 3)
        # df['dif']=df['short_ema']-df['long_ema']
        # df['dea']=np.round(talib.EMA(df['dif'].values, 9),3)
        # df['macd'] = 2 * (np.round(df['dif'] - df['dea'],3))

        return df

    # kdj
    @classmethod
    def kdj(self,df1):
        df=df1.copy()
        low_list =df['low'].rolling(window=9,min_periods=1).min()
        low_list.fillna(value=df['low'].expanding().min(), inplace=True)
        high_list = df['high'].rolling(window=9,min_periods=1).max()
        high_list.fillna(value=df['high'].expanding().max(), inplace=True)

        if len(high_list[high_list== low_list])==0:
            rsv = ((df['close'] - low_list) / (high_list - low_list) * 100)
        else:
            arr_t=high_list[high_list== low_list]
            arr_f=high_list[high_list!= low_list]
            rsv_f = ((df['close'][arr_f.index] - low_list[arr_f.index]) / (high_list[arr_f.index] - low_list[arr_f.index]) * 100)
            # rsv_t= ((df.loc[arr_t,['close']] - low_list[arr_t]) / (high_list[arr_t] - low_list[arr_t]) * 100)
            data= np.ones(len(arr_t))*100
            rsv_t=pd.Series(data,arr_t.index)
            rsv=pd.concat([rsv_f,rsv_t],axis=0,ignore_index=False).sort_index()

        df.loc[:,'k'] =np.round(rsv.ewm(com=2).mean(),3)
        df.loc[:,'d'] = np.round(df['k'].ewm(com=2).mean(),3)
        df.loc[:,'j'] = np.round(3 * df['k'] - 2 * df['d'],3)
        return df

    # rsi
    @classmethod
    def rsi(self,df):
        df["rsi_fast"] = talib.RSI(df['close'], timeperiod=9)
        df["rsi_slow"] = talib.RSI(df['close'], timeperiod=12)
        df["rsi_long"] = talib.RSI(df['close'], timeperiod=72)
        return df

    # atr
    @classmethod
    def atr(self,df):
        df['preclose']=df['close'].shift(1)
        df['preclose']=df['preclose'].fillna(method='bfill')
        df['tr']=df.apply(lambda x:max(x['high']-x['low'], abs(x['high'] - x['preclose']), abs(x['low'] - x['preclose'])),axis=1)
        df['atr'] = df['tr'].rolling(window=14, min_periods=1).mean()
        return df

    # mtm动量指标
    @classmethod
    def mtm(self,df,N=12, M=6):
        """
            MTM动力指标
        算法：
        MTM线　　当日收盘价与N日前的收盘价的差
        MTMMA线　对上面的差值求N日移动平均
        参数：N 间隔天数，也是求移动平均的天数，一般取6
        用法：
        1.MTM从下向上突破MTMMA，买入信号
        2.MTM从上向下跌破MTMMA，卖出信号
        3.股价续创新高，而MTM未配合上升，意味上涨动力减弱
        4.股价续创新低，而MTM未配合下降，意味下跌动力减弱
        5.股价与MTM在低位同步上升，将有反弹行情；反之，从高位同步下降，将有回落走势。
        """
        df['mtm'] = np.round(df['close'] - df['close'].shift(N),3)
        df['mtmma'] =np.round(df['mtm'].rolling(M).mean(),3)
        return df

    # boll
    @classmethod
    def boll(self,df):
        df['boll_up'], df['boll_mid'], df['boll_low'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        return df

    # bias
    @classmethod
    def bias(self,df):
        df['bias_short'] = (df['close'] - df['close'].rolling(6, min_periods=1).mean()) / df['close'].rolling(6,min_periods=1).mean() * 100
        df['bias_mid'] = (df['close'] - df['close'].rolling(12, min_periods=1).mean()) / df['close'].rolling(12,min_periods=1).mean() * 100
        df['bias_long'] = (df['close'] - df['close'].rolling(24, min_periods=1).mean()) / df['close'].rolling(24,min_periods=1).mean() * 100
        df['bias_short'] = round(df['bias_short'], 2)
        df['bias_mid'] = round(df['bias_mid'], 2)
        df['bias_long'] = round(df['bias_long'], 2)
        return df

    # 计算所有指标
    @classmethod
    def cal_indicator(self,df):
        df=  self.macd(df)
        df = self.sma(df)
        # df = self.kdj(df)
        df = self.rsi(df)
        df = self.boll(df)
        df = self.bias(df)
        return df

    # 计算即时kdj
    @classmethod
    def instant_kdj(self,high,low,close,k_pre,d_pre,df_bar):
        if high< df_bar['high'].max():
            high=df_bar['high'].max()
        if low> df_bar['low'].min():
            low=df_bar['low'].min()
        if high==low:
            rsv=100
        else:
            rsv=(close-low)/(high-low)*100
        k=(2/3*k_pre)+(1/3*rsv)
        d=(2/3*d_pre)+(1/3*k)
        j=(3*k)-(2*d)
        return np.round(k,3),np.round(d,3),np.round(j,3)

    @classmethod
    def ema(self,x,n,pre_y):
        return (2 * x + (n - 1) * pre_y) / (n + 1)

    # 计算即时macd
    @classmethod
    def instant_macd(self,price,pre_short_ema,pre_long_ema,pre_dea):
        short_ema = self.ema(price, 12, pre_short_ema)
        long_ema = self.ema(price, 26, pre_long_ema)
        dif = short_ema - long_ema
        dea = self.ema(dif, 9, pre_dea)
        macd = (dif - dea) * 2
        return (dif,dea,macd)

    # 计算即时boll
    @classmethod
    def instant_boll(self,close_19,price):
        close_20=np.append(close_19,price)
        boll_mid=np.mean(close_20,axis=0)
        # 求标准差
        arr_std = np.std(close_20, ddof=0)
        boll_up=boll_mid + 2 * arr_std
        boll_low = boll_mid - 2 * arr_std
        return boll_low,boll_mid,boll_up

    # 计算即时均值
    @classmethod
    def instant_sma(self,close_array,price):
        # arr=close_array[-n+1:]
        arr=np.append(close_array,price)
        ret=np.mean(arr)
        return ret

    # 计算即时mtm
    @classmethod
    def instant_mtm(self,pren_close,mtm5,price):
        mtm=np.round(price-pren_close,3)
        mtmma = np.round((mtm5 + mtm) / 6,3)
        return mtm,mtmma

if __name__=="__main__":
    # df = pro.query('daily', ts_code='002526.SZ', start_date='20110801', end_date='20200810')
    df = GmApi().getSymbolHistoryKdata('SHSE.601318', start_time='2022-04-01', end_time='2022-11-10')
    # df1 = Indicator.boll(df.copy())
    # df2=df.iloc[-20:-1,:].copy()

    # df['prenclose'] = df['close'].shift(6)
    # df['prenclose'].fillna(method='bfill',inplace=True)


    bol= Indicator.macd(df)
    # mtm=15.21-14.78
    # mtmma=(bol['mtm'].sum()+mtm)/6
    #
    print(bol)

    # macd=Indicator().instant_macd(38.46,38.234,39.015,-0.969)
    # print(macd)
    # bol=bol.tail(5)
    # mtmma=Indicator.instant_mtm(19.1739,bol['mtm'].sum(),19.92)
    # print(mtmma)
    # #
    # print(bol)
    # print(df)
    # df['k_pre'] = df['k'].shift(1)
    # df["k_pre"].fillna(method='bfill', inplace=True)
    # df['d_pre'] = df['d'].shift(1)
    # df["d_pre"].fillna(method='bfill', inplace=True)
    # # df=df.loc[(df['k'] >= df['d']) & (df['k_pre'] < df['d_pre'])]
    # df=df.loc[(df['k'] < df['d']) & (df['k_pre'] >= df['d_pre'])]
    # df.to_csv("e:\\300919.csv")
    # df.loc[(df['dif'] < df['dea']) & (df['dif_pre'] >= df['dea_pre']), ['signal']] = 0

    # 上向下突破上轨，买出
    # df.loc[(df['close_pre'] >= df['boll_up_pre']) & (df['close'] < df['boll_up']), ['signal']] = 0
    # print(df1.tail(10))
    # df['pre_close'] = df['close'].shift()
    # df["pre_close"].fillna(method='bfill', inplace=True)
    # df['change'] = (df['close'] - df['pre_close']) / df['pre_close']
    # df=Indicator.cal_indicator(df)
    # df.index=pd.to_datetime(df.index)
    # figure = mpyplot.figure(figsize=(20, 8), facecolor='#ffffff', edgecolor='#000000', linewidth=1)
    # plt= Plot_OldSync()
    # plt.plotfig(df=df,fig=figure)
    # plt.show()
    pass
    # print(df)
