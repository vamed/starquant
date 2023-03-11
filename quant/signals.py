# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:交易信号类
# Copyright (C) 2021-2023
###############################################################################
#
from quant.indicators import Indicator
class Signal():
    def __init__(self):
        pass
    # 止损
    @classmethod
    def buy_signal(self,df):
        df=self.kdj_signal(df)
        # df=self.boll_signal(df)
        return df

    # macd金叉
    @classmethod
    def macd_signal(self,df):
        df=Indicator.macd(df)
        df['dif_pre'] = df['dif'].shift(1)
        df["dif_pre"].fillna(method='bfill', inplace=True)
        df['dea_pre'] = df['dea'].shift(1)
        df["dea_pre"].fillna(method='bfill', inplace=True)
        df.loc[(df['dif'] >= df['dea']) & (df['dif_pre'] < df['dea_pre']), ['signal']] = 1
        df.loc[(df['dif'] < df['dea']) & (df['dif_pre'] >= df['dea_pre']), ['signal']] = 0
        df["signal"].fillna(method='ffill', inplace=True)
        return df

    # kdj金叉
    @classmethod
    def kdj_signal(self,df):
        df=Indicator.kdj(df)
        # print(df)
        df['k_pre'] = df['k'].shift(1)
        df["k_pre"].fillna(method='bfill', inplace=True)
        df['d_pre'] = df['d'].shift(1)
        df["d_pre"].fillna(method='bfill', inplace=True)
        df['j_pre'] = df['j'].shift(1)
        df["j_pre"].fillna(method='bfill', inplace=True)

        df.loc[(df['k'] >= df['d']) & (df['k_pre'] < df['d_pre']), ['signal']] = 1
        df.loc[(df['k'] < df['d']) & (df['k_pre'] >= df['d_pre']), ['signal']] = 0
        # df.loc[df['j']>100, ['signal']] = 0
        df["signal"].fillna(method='ffill', inplace=True)
        # print(df)
        return df

if __name__=="__main__":

    df=Signal().bt(symbol='SHSE.601318', start = '2022-03-01',end = '2022-11-05')
