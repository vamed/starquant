import numpy as np
# 获取历史数据
import datetime
import pytz
from gm.api import *
from quant.api.singleton import singleton
from quant.model.traderecord import TradeRecord
from quant.util import stringutil, stockutil, pdutil
from quant.util.configutil import get_config
import pandas as pd

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)

# 掘金接口
@singleton
class GmApi():
    # 拙金数据API封装
    def __init__(self):
        self.token=get_config('TOKEN','gmtoken')
        set_token(self.token)

    def getSymbolHistoryKdata(self,symbol,start_time=None,end_time=None,adjust=ADJUST_PREV,adjust_end_time=datetime.datetime.now()):

        df = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time,
                               fields='symbol, open, close, low, high,volume,amount,eob', adjust=adjust,adjust_end_time=adjust_end_time, df=True)

        df['date']=df['eob'].apply(lambda x:x.strftime('%Y-%m-%d'))
        # df=self.calc_atr(df)
        df=df.set_index(['date'])

        # loginfo(df)
        # df1=df.shift()
        # df1.fillna(method='backfill',inplace=True)
        # df['preclose']=df1['close']
        # df['change']=(df['preclose']-df['close'])/df['close']
        # loginfo(df)
        return df

    # 获取历史数据
    def getHistoryData(self,symbol,start_time=None,end_time=None,adjust=ADJUST_PREV,adjust_end_time=datetime.datetime.now()):

        df = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time,
                               fields='symbol, open, close, low, high,volume,amount,eob', adjust=adjust,adjust_end_time=adjust_end_time, df=True)

        df['date']=df['eob'].apply(lambda x:x.strftime('%Y-%m-%d'))
        return df

    # 获取历史数据前N条数据
    def getHistoryNKdata(self,symbol,count=250,end_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        df = history_n(symbol=symbol, frequency='1d', count=count, end_time=end_date,
                                   fields='symbol, open, close, low, high,volume,amount, eob', adjust=ADJUST_PREV, df=True)
        if df.columns.__contains__('eob')==False:
            print(symbol)
        df['date'] = df['eob'].apply(lambda x: x.strftime('%Y-%m-%d'))
        return df

    # 获取一段时间内的交易日期
    def get_trade_calendar(self,start_date,end_date):
        return get_trading_dates(exchange='SZSE', start_date=start_date, end_date=end_date)

    def get_history_current_data(self,symbol,start_time=None,end_time=None):
        history_data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time,
                               fields='open, close,volume,amount, low, high, eob', adjust=ADJUST_PREV, df=True)

        current_data=self.get_current_data(symbol=symbol)
        history_data=history_data.append(current_data)
        history_data['date'] = history_data['eob'].dt.strftime('%Y-%m-%d')
        history_data.set_index(keys=['date'],inplace=True)
        history_data.index = pd.to_datetime(history_data.index)
        return history_data

    #获取掘金历史数据 backtest数据格式
    def get_bt_history_data(self,symbol,start_time=None,end_time=None):
        today=datetime.datetime.now().strftime('%Y-%m-%d')

        if end_time==None:
            end_time=today

        if end_time>today:
            end_time=today

        if start_time==None:
            start_time=(datetime.datetime.strptime(end_time, '%Y-%m-%d').date()-datetime.timedelta(days=720)).strftime('%Y-%m-%d')

        fields = 'open,close,volume,low,high,eob'
        history_data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time,
                               fields=fields, adjust=ADJUST_PREV, df=True)

        if end_time==today:
            time_now = datetime.datetime.now().strftime('%H:%M')
            if (time_now >= "09:30") & (time_now <= "15:30"):
            # if (time_now >= "09:30"):
                current_data = self.get_current_data(symbol=symbol)
                current_data=current_data.loc[:,fields.split(',')]
                history_data = history_data.append(current_data)

        history_data['date'] = history_data['eob'].dt.strftime('%Y-%m-%d')
        # history_data['datetime'] = history_data['eob'].apply(lambda x: x.strftime('%Y-%m-%d'))
        history_data['volume'] =  history_data['volume']
        history_data['openinterest'] = 0
        # history_data.drop('eob', axis=1, inplace=True)
        # history_data['date']=pd.to_datetime(history_data['date'])
        history_data.drop_duplicates(subset='date',keep='first',inplace=True)
        history_data.set_index(keys=['date'],inplace=True)
        history_data.index = pd.to_datetime(history_data.index)
        return history_data

    # 获取当然数据
    def get_current_data(self,symbol):
        current_data = current(symbols=symbol, fields='open, price,cum_volume,cum_amount, low, high, created_at')
        # print(current_data)
        df = pd.DataFrame(current_data)
        df.rename(columns={"price": "close", "cum_volume": "volume", "cum_amount": "amount", "created_at": "eob"}, inplace=True)

        return df

    # 获取当然数据
    def get_current_close(self,symbol):
        current_data = current(symbols=symbol, fields='symbol,open, price,cum_volume,cum_amount, low, high, created_at')
        # print(current_data)
        df = pd.DataFrame(current_data)
        df.rename(columns={"price": "close", "cum_volume": "volume", "cum_amount": "amount", "created_at": "eob"}, inplace=True)

        return df

    # 获取股票的pe
    def get_pe(self,symbols):
        symbs=[]
        for s in symbols:
            if (s[5]=='0') or (s[5]=='6'):
                symbs.append(s)
        date=get_previous_trading_date(exchange='SZSE', date=datetime.datetime.now())
        df = get_fundamentals(table='trading_derivative_indicator', symbols=symbs, start_date=date,
                              end_date=date,
                              fields='TCLOSE,NEGOTIABLEMV,TOTMKTCAP,TURNRATE,PELFY,PETTM,PEMRQ,PELFYNPAAEI,PETTMNPAAEI',
                              df=True)
        df.drop_duplicates(keep='last',inplace=True)
        if len(df)>0:
            df['code']=df['symbol'].apply(lambda x:x.split('.')[1])
            df=df.loc[:,['code','PEMRQ']]
            df.set_index('code',inplace=True)
        return df

    # # 获取股票信息例如名称
    # def get_stock_info(self):
    #     df = get_instruments(exchanges='SZSE,SHSE', sec_types=1, df=True)
    #     df=df.loc[:,['symbol','sec_type','sec_id','listed_date','exchange','sec_name']]
    #     df.rename(columns={"sec_type": "type", "sec_id": "code", "listed_date": "listdate", "sec_name": "name"}, inplace=True)
    #
    #     StockInfo().batchInsert(df)
    #     pass

    def get_day_bar(self,symbol,date,mode):
        # end_date=date+datetime.timedelta(days=1)
        # df = history_n(symbol=symbol, frequency='60s', count=240, end_time=end_date.strftime('%Y-%m-%d'),adjust=ADJUST_PREV, df=True)
        # # df=
        # df = df.loc[df['eob'] > date.strftime('%Y-%m-%d'), :]
        date_str=date.strftime('%Y-%m-%d')
        df=self.get_day_minute_data(symbol=symbol,date=date_str)

        # 实盘在交易时间补齐盘前数据
        time_str=date.strftime('%H:%M')
        if (time_str>="09:30") and (time_str<="15:00") and (mode==MODE_LIVE):
            df_pre = GmApi().get_pre_open_bar(symbol=symbol, date=date.strftime("%Y-%m-%d"))
            df=pd.concat([df_pre,df],ignore_index=True)

        return df

    # 查询基本面数据
    def getfundamental(self,symbols,start_date,end_date):
        df=get_fundamentals(table='trading_derivative_indicator', symbols=symbols,
                         start_date=start_date, end_date=end_date,
                         fields='TCLOSE,NEGOTIABLEMV,TOTMKTCAP,TURNRATE,PELFY,PETTM,PEMRQ,PELFYNPAAEI,PETTMNPAAEI',
                         df=True)
        df['date'] = df['pub_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        df = df.set_index(['date'])
        return df

    # 获取基本面信息
    def get_fundamentals(self,table, symbols, start_date,end_date, fields,df=True):
        # df = get_fundamentals(table=table, symbols=symbols, start_date=start_date,
        #                       end_date=end_date, fields=fields,
        #                       df=df)
        if self.token=="1aa9d5d2fba51059d0c8c24c258df9cbf7916548":
            ret= get_fundamentals(table=table, symbols=symbols, start_date=start_date,
                             end_date=end_date, fields=fields,
                             df=df)
        else:
            ret=pd.DataFrame()
            for s in symbols:
                ret_=get_fundamentals(table=table, symbols=s, start_date=start_date,
                             end_date=end_date, fields=fields,
                             df=df)
                if len(ret)==0:
                    ret=pd.DataFrame(columns=ret_.columns)
                ret=pd.concat([ret,ret_],axis=0)
        return ret

    #获取上一交易日
    def get_last_trade_date(self):
        date=get_previous_trading_date(exchange='SZSE', date=datetime.datetime.now().strftime("%Y-%m-%d"))
        return pd.to_datetime(date)

    # 获取上一交易日
    def get_previous_trading_date(self,market="SHSE",date=datetime.datetime.now().strftime("%Y-%m-%d")):
        return get_previous_trading_date(market, date)

    # 获取某天分钟数据
    def get_day_minute_data(self,symbol,date):
        start="%s 09:00:00"%(date)
        end="%s 15:10:00"%(date)
        df = history(symbol=symbol, frequency='60s', start_time=start,
                     end_time=end, df=True)
        return df

    # 获取每天早盘前成交数据
    def get_pre_open_bar(self,symbol,date):
        start="%s 09:25:00"%(date)
        end="%s 09:29:00"%(date)
        df = history(symbol=symbol, frequency='tick', start_time=start,
                     end_time=end,adjust=ADJUST_PREV, df=True)
        df=df.loc[((df['last_amount']>0) & (df['last_volume']>0)),: ]
        df.rename(columns={'price':'close','last_amount':'amount','last_volume':'volume'},inplace=True)
        # df['eob']= datetime.datetime.strptime("{} 09:30:00+08:00".format(date),"%Y-%m-%d %H:%M:%S%z").astimezone(pytz.timezone("Asia/Shanghai"))
        # df['bob'] =datetime.datetime.strptime("{} 09:29:00+08:00".format(date),"%Y-%m-%d %H:%M:%S%z").astimezone(pytz.timezone("Asia/Shanghai"))
        df['eob']=pytz.timezone("Asia/Shanghai").localize(datetime.datetime.strptime("{} 09:30:00".format(date),"%Y-%m-%d %H:%M:%S"))
        df['bob'] =pytz.timezone("Asia/Shanghai").localize(datetime.datetime.strptime("{} 09:29:00".format(date),"%Y-%m-%d %H:%M:%S"))
        df['frequency'] = '60s'
        df['position'] = '0'
        df['pre_close'] = '0'
        df['receive_local_time'] =np.NAN

        df = df.loc[0:1,['symbol','eob','bob','open','close','high', 'low', 'volume', 'amount', 'pre_close','position','frequency', 'receive_local_time']]
        return df

    # 获取最近的交易日期
    def get_lastday_data(self,symbols):
        symbol= stringutil.array_to_string(symbols)
        start = datetime.datetime.now()
        if (start.hour>=15) and stockutil.isTradeDate(start.strftime("%Y-%m-%d")):
            current_data = current(symbols=symbol, fields='symbol,open, price, low, high, created_at')
            df = pd.DataFrame(current_data)
            df.rename(columns={"price": "close", "created_at": "eob"}, inplace=True)
        else:
            start = stockutil.get_last_trade_date()
            end=(start + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            df = history(symbol=symbol, frequency='1d', start_time=start.strftime("%Y-%m-%d"),
                               end_time=end,
                               fields='symbol,open, close, low, high, eob', adjust=ADJUST_PREV, df=True)
        # df.set_index('symbol',inplace=True,drop=True)
        return df
    # 获取历史数据前N条数据 abupy格式
    # def getHistoryNKdata(self,symbol,count=250):
    #     df = history_n(symbol=symbol, frequency='1d', count=count, end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #                                fields='symbol, open, close, low, high,volume, eob', adjust=ADJUST_PREV, df=True)
    #     df['date'] = df['eob'].apply(lambda x: x.strftime('%Y-%m-%d'))
    #     return df
    # 盘后更新当天交易记录
    def update_execution_reports(self):
        df = get_execution_reports()
        df = pd.DataFrame(df)
        # print(df)
        TradeRecord().batch_insert(df)
        return df

    #获取分红信息
    def get_dividend(self,symbol, start_date, end_date=None):
        df = get_dividend(symbol, start_date, end_date=end_date, df=True)
        return df

    # 获取除权系数
    def get_xr_coefficient(self,symbol,start_time,end_time):
        df = GmApi().getSymbolHistoryKdata(symbol=symbol, start_time=start_time, end_time=end_time)
        df_div=GmApi().get_dividend(symbol, start_time, end_time)
        df['xr_coefficient']=1
        for i,row in df_div.iterrows():
            div_index=df['eob']<row['created_at']
            close=df.loc[div_index==True,:].iat[-1,2]
            if row['cash_div']>0:
                df.loc[div_index,'xr_coefficient']+=df.loc[div_index,'xr_coefficient']*(row['cash_div']/close)
            if row['share_div_ratio']>0:
                df.loc[div_index,'xr_coefficient']+=df.loc[div_index,'xr_coefficient']*(1+row['share_div_ratio'])
            if row['share_trans_ratio']>0:
                df.loc[div_index,'xr_coefficient']+=df.loc[div_index,'xr_coefficient']*(1+row['share_trans_ratio'])

        return df

    #计算除权历史K线数据
    def getSymbolXrHistoryKdata(self,symbol, start_time, end_time):
        df = GmApi().getSymbolHistoryKdata(symbol=symbol, start_time=start_time, end_time=end_time)
        df_turnrate = GmApi().get_fundamentals(symbols=symbol, start_date=start_time, end_date=end_time)
        df_div=GmApi().get_dividend(symbol, start_time, end_time)
        df['ma_price0'] = df['amount'] / df['volume']
        for i,row in df_div.iterrows():
            div_index=df['eob']<row['created_at']
            if row['cash_div']>0:
                df.loc[div_index,'amount']=df.loc[div_index,'amount']*(1-row['cash_div']/df.loc[div_index,'close'])
                df['ma_price1'] = df['amount'] / df['volume']
            if row['share_div_ratio']>0:
                df.loc[div_index,'volume']=df.loc[div_index,'volume']*(1+row['share_div_ratio'])
            if row['share_trans_ratio']>0:
                df.loc[div_index,'volume']=df.loc[div_index,'volume']*(1+row['share_trans_ratio'])
                df['ma_price2'] = df['amount'] / df['volume']

        # df['ma_price'] = df['amount'] / df['volume']
        df['turnoverrate'] = df_turnrate['TURNRATE']
        return df

    # 财务信息
    def get_finance(self,symbol):
        df=get_fundamentals(table='deriv_finance_indicator', symbols=symbol,
                         start_date='2021-01-01', end_date='2022-11-25',
                         fields='QUICKRT,CURRENTRT, ASSLIABRT,TATURNRT,FATURNRT,INVTURNRT,ACCRECGTURNRT,ROEANNUAL,EPSDILUTEDNEWP,SGPMARGIN,NPTOAVGTA,NOPCAPTURNRT,NPGRT',
                         df=True)

        return df


    def get_close(self,symbol,date,adjust_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        df = history_n(symbol=symbol, frequency='1d', count=2, end_time=date,
                                   fields='symbol, open, close, low, high, eob', adjust=ADJUST_PREV,adjust_end_time=adjust_end_time, df=True)

        price = df.at[df.index[-1], 'close']
        return price

    def get_tick_close(self,symbol,date,adjust_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        df = history_n(symbol=symbol, frequency='60s', count=2, end_time=date,
                                   fields='symbol, open, close, low, high, eob', adjust=ADJUST_PREV,adjust_end_time=adjust_end_time, df=True)

        price = df.at[df.index[-1], 'close']
        return price

    def get_current_price(self,symbol):
        ret = current(symbols=symbol, fields='')

        return ret[0].price

    def get_prev_trading_date(self,date):
        return get_previous_trading_date("SHSE",date)

    def get_trade_dates(self):
        days=get_trading_dates(exchange='SHSE', start_date='2022-01-01', end_date='2023-12-30')
        return days

    # 获取上证指数昨日收盘价
    def get_sh_index_pre_close(self,date=datetime.datetime.now()):
        pre_date= get_previous_trading_date("SHSE",date=date.strftime("%Y-%m-%d"))
        df = history_n(symbol='SHSE.000001', frequency='1d', count=1, end_time=pre_date,
                                   fields='symbol, open, close, low, high, eob', adjust=ADJUST_PREV, df=True)
        return df['close'].values[0]

if __name__=='__main__':
    # print(GmApi().get_sh_index_pre_close())
    # days=GmApi().get_trade_dates()
    df= GmApi().getHistoryNKdata(symbol='SHSE.600030',count=1)
    print(df)
