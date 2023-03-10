# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:选股类
# Copyright (C) 2021-2023
###############################################################################
#

import sys,os
import pandas as pd
from quant.api.gmapi import GmApi
from quant.enums.ratings import Ratings
from quant.enums.strategys import Strategys
from quant.util import stockutil

base_dir=os.path.dirname(os.path.dirname(__file__))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中
from gm.enum import MODE_BACKTEST
from quant.model.stockpool import StockPool
# 择时
class Picker():
    #     获取择时股票列表
    def get_picktime(self,context,codes=[]):
        account_type=context.setting.account_type
        count=50-len(context.positions)
        if len(codes)==0:
            if context.mode==MODE_BACKTEST:
                df = StockPool().get_picktime()
                df = df.head(count)

            df.drop_duplicates(subset='code', keep='first', inplace=True)

        else:
            df=Picker().picktime_by_codes(codes)
        df.reset_index(drop=True,inplace=True)
        df = df.head(count)
        return df
    #
    def picktime_by_codes(self,codes=[]):
        df=pd.DataFrame(columns=['symbol','code','name','change','price','close', 'strategy', 'rating', 'date'])
        for code in codes:
            df_symbol= GmApi().getHistoryNKdata(symbol=stockutil.getGmSymbol(code),count=1)
            if len(df_symbol)>0:
                df_symbol['code'] = df_symbol['symbol'].apply(lambda x: stockutil.delSymbolPrefix(x))
                df_symbol['name'] = ''
                df_symbol['change'] = 0
                df_symbol['price'] = df_symbol['close']
                df_symbol['strategy'] = Strategys.MeanRevertingStrategy.value
                df_symbol['rating'] = Ratings.BuyIn.value
                df_symbol['date'] = df_symbol['eob']
                df_symbol = df_symbol.loc[:,
                            ['symbol', 'code', 'name', 'change', 'price', 'close', 'strategy', 'rating', 'date']]
                df=pd.concat([df,df_symbol],ignore_index=True,axis=0)

        df.drop_duplicates(subset=['symbol'],keep='first',inplace=True)
        return df

if __name__=='__main__':
    df=Picker().picktime_by_codes(codes=['002281','002272'])
    print(df)
    pass