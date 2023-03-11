# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:交易统计分析类
# Copyright (C) 2021-2023
###############################################################################
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gm.enum import ADJUST_NONE, ADJUST_PREV

from quant.api.gmapi import GmApi
from quant.empyrical import stats
from quant.model.order import Order

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)
pd.options.mode.chained_assignment = None
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

class Metric():
    """市场中1年交易日，默认250日"""
    g_market_trade_year = 250
    def __init__(self):
        self.capital=1000000
        self.benchmark='SHSE.000001'
        pass

    def stat(self,account_id="back_test20221113153909",start=None,end=None):
        # account_id = "back_test20221212163953"
        # account_id =account_id
        df_trade = Order().getRecord(account_id=account_id)
        profit_rates=np.array(0)
        profits=np.array(0)
        df_unclose=pd.DataFrame(columns=df_trade.columns)
        self.close_count=0
        self.unclose_count=0
        self.total_buy_amount=0

        # 单股持仓数天
        keepdays=[]
        for symbol in set(df_trade['symbol']):
            df_symbol=df_trade.loc[df_trade['symbol']==symbol,:]
            df_symbol.reset_index(inplace=True,drop=True)
            symbol_profit_rates,symbol_profits,symbol_df_close,symbol_df_unclose,df_sell=self.symbol_trade_stat(df_symbol)
            if len(df_sell)>0:
                keepdays=np.append(keepdays,df_sell['keepdays'].values)

            profit_rates=np.append(profit_rates,symbol_profit_rates)
            profits = np.append(profits, symbol_profits)
            self.close_count +=len(symbol_df_close)
            self.unclose_count +=len(symbol_df_unclose)
            if len(symbol_df_close)>0:
                self.total_buy_amount+=symbol_df_close['amount'].sum()
            df_unclose=pd.concat([symbol_df_unclose,df_unclose])

        # print(df_unclose)
        # 清仓盈利统计
        self.max_keepdays=keepdays.max()
        self.median_keepdays =np.median(keepdays)
        self.close_profit=profits.sum()
        self.close_profit_rate = self.close_profit/self.total_buy_amount
        # 持仓盈利统计
        last_date=df_trade['trade_date'].max()
        df_unclose['close']=0
        for symbol in set(df_unclose['symbol']):
            df_price= GmApi().getHistoryNKdata(symbol,count=1,end_date=last_date)
            df_unclose.loc[df_unclose['symbol']==symbol,['close']]=df_price.at[df_price.index[-1],'close']

        self.unclose_profit=((df_unclose['close']-df_unclose['price'])*df_unclose['volume']).sum()
        # 累计总收益
        self.total_profit=self.close_profit+self.unclose_profit
        # 总收益率
        self.total_profit_rate=self.total_profit/self.capital*100
        self.win_rate=0
        # 胜率
        arr_win=profit_rates[np.where(profit_rates> 0)]
        arr_lost = profit_rates[np.where(profit_rates <= 0)]
        if (len(arr_win)+len(arr_lost))>0:
            self.win_rate=len(arr_win)/(len(arr_win)+len(arr_lost))
        #平均获利期望
        self.gains_mean = 0
        if len(arr_win) > 0:
            self.gains_mean = np.mean(arr_win)
        #平均亏损期望
        self.losses_mean=0
        if len(arr_lost)>0:
            self.losses_mean=np.mean(arr_lost)
        # 盈亏比
        self.win_loss_profit_rate=1 if self.losses_mean == 0 else -round(self.gains_mean / self.losses_mean, 4)
        # =======================base stat===============================================================================
        df_benmark = self.get_benchmark_returns(start_time=df_trade['trade_date'].min(),
                                                    end_time=df_trade['trade_date'].max(),symbol=self.benchmark)
        benchmark_returns = df_benmark['change'].values
        # 从交易记录统计每天收益明细
        df_profit = self.get_profit(df_trade)
        self.max_position=df_profit['cum_amount'].max()
        self.mean_position = df_profit['cum_amount'].mean()

        df_profit['profit_rate']=df_profit['profit']/self.capital
        # df_profit['profit'] = df_profit['profit'] / capital
        max_drawdown, start, end=self.get_max_drawdown(df_profit['profit_rate'])
        # print(max_drawdown)
        algorithm_returns = df_profit['profit_rate'].values

        # print(algorithm_returns.mean())
        # print(algorithm_returns.std())
        self.base_stats(benchmark_returns, algorithm_returns)

    # 计算回撤
    def get_max_drawdown(self,returns):
        """Assumes returns is a pandas Series"""
        ret = returns.add(1).cumprod()
        drawdown = ret.div(ret.cummax()).sub(1)
        max_drawdown = drawdown.min()
        end = drawdown.argmin()
        start = ret[:end].argmax()
        return max_drawdown, start, end

    # 打印输出统计数据
    def print_stat(self):
        print('买入后卖出的交易数量:{}'.format(self.close_count))
        print('买入后尚未卖出的交易数量:{}'.format(self.unclose_count))
        print('单日最大持仓金额:{:.2f}'.format(self.max_position))
        print('日均持仓金额:{:.2f}'.format(self.mean_position))
        print('策略持股最大天数:{:.2f}'.format(self.max_keepdays))
        print('策略持股天数中位数:{:.2f}'.format(self.median_keepdays))

        print('已清仓总收益:{:.2f}'.format(self.close_profit))
        print('持仓总收益:{:.2f}'.format(self.unclose_profit))
        print('累计总收益:{:.2f}'.format(self.total_profit))
        print('累计总收益率:{:.2f}%'.format(self.total_profit_rate))
        # 交易额收益率: 16.39 %
        # print('交易额收益率:{:.2f}%'.format(self.profit_rate*100))
        # print('策略持股天数平均值:{:.2f}'.format(self.keep_days_mean))
        # print('策略持股天数中位数:{:.2f}'.format(self.keep_days_median))
        print('胜率:{:.2f}%'.format(self.win_rate * 100))
        print('平均获利期望:{:.2f}%'.format(self.gains_mean * 100))
        print('平均亏损期望:{:.2f}%'.format(self.losses_mean * 100))
        print('盈亏比:{:.2f}'.format(self.win_loss_profit_rate))

        print('alpha阿尔法:{:.2f}'.format(self.alpha))
        print('beta贝塔:{:.2f}'.format(self.beta))
        print('Information信息比率:{:.2f}'.format(self.information))

        print('策略Sharpe夏普比率: {:.2f}'.format(self.algorithm_sharpe))
        print('基准Sharpe夏普比率: {:.2f}'.format(self.benchmark_sharpe))

        print('策略波动率Volatility: {:.2f}'.format(self.algorithm_volatility))
        print('基准波动率Volatility: {:.2f}'.format(self.benchmark_volatility))
        print('最大回撤max_drawdown: {:.2f}%'.format(self.max_drawdown*100))

        print('交易总天数: {:.2f}'.format(self.num_trading_days))
        print('年化收益: {:.2f}%'.format(self.algorithm_annualized_returns*100))
        print('基准年化收益: {:.2f}%'.format(self.benchmark_annualized_returns*100))

    # 将单股票交易记录拆分成买入全买出数据、卖出数据、未成交数据
    def divide_symbol_trade_record(self,df_trade):
        df_buy=df_trade.loc[df_trade['side'] == 1, :].copy()
        df_buy.reset_index(drop=True,inplace=True)
        df_buy['cum_buy_amount']=df_buy['amount'].cumsum()
        df_buy['cum_buy_volume'] = df_buy['volume'].cumsum()
        df_sell=df_trade.loc[df_trade['side'] == -1, :].copy()
        df_sell.reset_index(drop=True, inplace=True)
        df_sell['cum_sell_amount'] = df_sell['amount'].cumsum()
        df_sell['cum_sell_volume'] = df_sell['volume'].cumsum()
        sellout_volume=0
        buy_volume=0
        df_close=pd.DataFrame()
        df_unclose=pd.DataFrame()
        if len(df_sell)>0:
            sellout_volume=df_sell.at[df_sell.index[-1],'cum_sell_volume']
        if len(df_buy) > 0:
            buy_volume=df_buy.at[df_buy.index[-1],'cum_buy_volume']
        # 买入交易全部卖出
        unclose_count = 0
        if buy_volume==sellout_volume:
            close_count=len(df_sell)
            df_close = df_buy.head(close_count)
            total_buy_amout=  df_buy.at[df_buy.index[-1],'cum_buy_amount']
        #     部分卖出
        else:
            if len(df_buy)>0:
                df_unclose=df_buy.loc[df_buy['cum_buy_volume']>sellout_volume,:]
                unclose_count=len(df_unclose)
            close_count=len(df_buy)-unclose_count
            df_close = df_buy.head(close_count)
            # 上一单完整卖出
            if df_buy.at[df_buy.index[close_count-1],'cum_buy_volume']==sellout_volume:
                # close_count=len(df_buy)-unclose_count
                total_buy_amout = df_buy.at[df_buy.index[-(unclose_count+1)], 'cum_buy_amount']
            #     最后一卖单只卖出上一买单部分
            else:
                divided_close= df_buy.loc[df_buy.index[close_count],:].copy()
                divided_unclose = df_buy.loc[df_buy.index[close_count], :].copy()
                divided_unclose['volume']=df_buy.at[df_buy.index[close_count], 'cum_buy_volume']-sellout_volume
                divided_unclose['amount']=divided_unclose['price']*divided_unclose['volume']
                df_unclose=df_unclose.append(divided_unclose)
                divided_close['volume']=df_buy.at[df_buy.index[close_count], 'volume']-(df_buy.at[df_buy.index[close_count], 'cum_buy_volume']-sellout_volume)
                divided_close['amount'] = divided_close['price'] * divided_close['volume']
                df_close=df_close.append(divided_close)
                # total_buy_amout =df_buy.at[df_buy.index[-unclose_count], 'cum_buy_amount']-(df_buy.at[df_buy.index[-unclose_count], 'cum_buy_volume']-sellout_volume)*df_buy.at[df_buy.index[-unclose_count], 'price']
        # print(df_sell)
        # print(df_close)
        df_close_copy=df_close.copy()
        df_sell['buy_time']=''
        df_sell['buy_volume'] = df_sell['volume']
        if len(df_close_copy)>0:
            total_buy_amout=df_close_copy['amount'].sum()
            for i,row_sell in df_sell.iterrows():
                for j,row_buy in df_close_copy.iterrows():
                    row_sell['buy_volume']=df_sell.at[i,'buy_volume']
                    if row_buy['volume']==0:
                        continue
                    if row_buy['volume']>=row_sell['buy_volume']:
                        df_close_copy.at[j,'volume']=row_buy['volume']-row_sell['buy_volume']
                        df_sell.at[i,'buy_time']=row_buy['trade_time']
                        break
                    else:
                        df_close_copy.at[j,'volume']=0
                        df_sell.at[i,'buy_volume']=row_sell['buy_volume']-row_buy['volume']

        # 计算持仓天数
        # df_sell['keepdays']=df_sell.apply(lambda x:datetimeutil.count_differ_days(pd.to_datetime(x['trade_time']),pd.to_datetime(x['buy_time'])),axis=1)
        if len(df_sell)>0:
            df_sell['keepdays'] = df_sell.apply(
                lambda x: (pd.to_datetime(x['trade_time'])-pd.to_datetime(x['buy_time'])).days,
                axis=1)

        # print(df_sell)
        return df_close,df_unclose,df_sell

#     按清仓次数统计
    def symbol_close_stat(self,df_buy,df_sell):
        columns=['symbol','side','price','volume','amount','trade_time','trade_date']
        df=pd.concat([df_buy.loc[:,columns],df_sell.loc[:,columns]],axis=0)
        df.sort_values(by='trade_time',inplace=True)
        df.reset_index(inplace=True,drop=True)

        df['cum_volume']=(df['side']*df['volume']).cumsum()
        df_close=df.loc[df['cum_volume']==0,:]
        i_last=0
        close_count=0
        profit_rates=[]
        profits=[]

        for i,row in df_close.iterrows():
            df_temp=df.loc[i_last:i,:]
            i_last=i+1
            close_count+=1
            profit=(df_temp.loc[df_temp['side'] == -1, ['amount']].sum()-df_temp.loc[df_temp['side']==1,['amount']].sum())['amount']
            profits.append(profit)
            if df_temp['amount'].sum()==0:
                profit_rates.append(0)
            else:
                profit_rates.append(profit/df_temp['amount'].sum())

        profit_total=np.sum(profits)
        # 盈利比率
        # profit_rate= profit_total/df.loc[df['side'] == 1, ['amount']].sum()['amount']
        return np.array(profit_rates),np.array(profits)

    # 单股票交易收益统计
    def symbol_trade_stat(self,df_symbol):
        df_close, df_unclose, df_sell = Metric().divide_symbol_trade_record(df_symbol)
        if df_sell['volume'].sum()!=df_close['volume'].sum():
            print('df_close与df_sell数量不配，数据出错')
        # close_count = len(df_close)
        # unclose_count = len(df_unclose)
        # # 清仓盈利统计
        # close_profit = df_sell['amount'].sum() - df_close['amount'].sum()
        # 总收益
        profit_rates=0
        profits=0
        if len(df_close)>0:
            profit_rates,profits = Metric().symbol_close_stat(df_close, df_sell)
        return profit_rates,profits,df_close,df_unclose, df_sell

    # 获取每日收益
    def get_profit(self, df_trade):
        start = df_trade['trade_date'].min()
        end = df_trade['trade_date'].max()
        df_sh = GmApi().getHistoryData(symbol='SHSE.000001', start_time=start, end_time=end)
        df=pd.DataFrame(index=df_sh['date'])
        df['profit'] = 0
        df['cum_amount'] = 0
        for symbol in set(df_trade['symbol'].values):
            df_symbol = df_trade.loc[df_trade['symbol'] == symbol, :].copy()
            df_symbol_profit= self.get_symbol_profit(df_symbol)
            df['profit']=df['profit']+df_symbol_profit['profit']
            df['profit'].fillna(value=0, inplace=True)
            df['cum_amount'] = df['cum_amount'] + df_symbol_profit['cum_amount']
            df['cum_amount'].fillna(value=0, inplace=True)
        # print(df)
        return df

    # 获取基准回报
    def get_benchmark_returns(self,start_time,end_time,symbol='SHSE.000001'):
        df_benmark = GmApi().getSymbolHistoryKdata(symbol, start_time=start_time,
                                             end_time=end_time)
        df_benmark['change'] = df_benmark['close'].pct_change(periods=1)
        df_benmark['change'].fillna(value=0,inplace=True)
        ret=df_benmark
        if symbol!='SHSE.000001':
            df_sh = GmApi().getHistoryData(symbol='SHSE.000001', start_time=start_time, end_time=end_time)
            df_temp = df_sh.copy()
            df_temp.drop_duplicates(subset=['date'], keep='first', inplace=True)
            df_temp.set_index('date', inplace=True)

            df_total = pd.DataFrame(index=df_temp.index)
            df_total['change'] = df_benmark['change']
            ret=df_total

        # benchmark_returns = df_benmark['change'].values
        return ret

    # 基础（风险）统计
    def base_stats(self,benchmark_returns,algorithm_returns):
        """度量真实成交了的capital_pd，即涉及资金的度量"""
        # # 平均资金利用率
        # 收益cum数据
        # noinspection PyTypeChecker
        self.algorithm_cum_returns = stats.cum_returns(algorithm_returns)
        self.benchmark_cum_returns = stats.cum_returns(benchmark_returns)

        # 最后一日的cum return
        self.benchmark_period_returns = self.benchmark_cum_returns[-1]
        self.algorithm_period_returns = self.algorithm_cum_returns[-1]

        # 交易天数
        self.num_trading_days = len(benchmark_returns)

        # 年化收益
        self.algorithm_annualized_returns = \
            (self.g_market_trade_year / self.num_trading_days) * self.algorithm_period_returns
        self.benchmark_annualized_returns = \
            (self.g_market_trade_year / self.num_trading_days) * self.benchmark_period_returns

        # 策略平均收益
        # 波动率
        self.benchmark_volatility = stats.annual_volatility(benchmark_returns)
        # noinspection PyTypeChecker
        self.algorithm_volatility = stats.annual_volatility(algorithm_returns)

        # 夏普比率
        self.benchmark_sharpe = stats.sharpe_ratio(benchmark_returns)
        # noinspection PyTypeChecker
        self.algorithm_sharpe = stats.sharpe_ratio(algorithm_returns)

        # 信息比率
        # noinspection PyUnresolvedReferences
        self.information = stats.information_ratio(algorithm_returns, benchmark_returns)

        # 阿尔法, 贝塔
        # noinspection PyUnresolvedReferences
        self.alpha, self.beta = stats.alpha_beta_aligned(algorithm_returns, benchmark_returns)

        # 最大回撤
        # noinspection PyUnresolvedReferences
        self.max_drawdown = stats.max_drawdown(algorithm_returns)

    # 获取单股票收益统计
    def get_symbol_profit(self,df_symbol):
        # print(df_symbol)
        df_buy=df_symbol.loc[df_symbol['side']==1,:].copy()
        df_buy_date=df_buy.groupby(by='trade_date').agg({'volume':np.sum,'amount':np.sum,})
        df_buy_date['price']=df_buy_date['amount']/df_buy_date['volume']
        # print(df_buy_date)
        df_sell=df_symbol.loc[df_symbol['side']==-1,:].copy()
        df_sell_date = df_sell.groupby(by='trade_date').agg({'volume': np.sum, 'amount': np.sum, })
        df_sell_date['price'] = df_sell_date['amount'] / df_sell_date['volume']

        df_symbol['side_amount']=df_symbol['side']*df_symbol['amount']*-1
        df_symbol['side_volume'] = df_symbol['side'] * df_symbol['volume']
        df_date=df_symbol.groupby(by='trade_date').agg({'side_volume':np.sum,'side_amount':np.sum,})
        df_date['cum_volume']=df_date['side_volume'].cumsum()
        # print(df_date)
        # df_date['cum_amount'] = df_date['side_amount'].cumsum()
        # df_date['pct_change']=df_date['cum_amount'].pct_change()
        # df_date['pct_change'].fillna(value=0,inplace=True)
        # print(df_date)
        df = GmApi().getHistoryData(symbol=df_symbol['symbol'].values[0], start_time=df_symbol['trade_date'].min(), end_time=df_symbol['trade_date'].max(),adjust=ADJUST_PREV)
        df.set_index('date',drop=True,inplace=True)
        df['pre_price']=df['close'].shift(1)
        df['pre_price'].fillna(method="bfill", inplace=True)
        df['price_change']=df['close']-df['pre_price']
        df['pct_change']=df['close'].pct_change()
        df['pct_change'].fillna(value=0, inplace=True)

        df['buy_price']=df_buy_date['price']
        df['buy_volume'] = df_buy_date['volume']
        df['sell_price'] = df_sell_date['price']
        df['sell_volume'] = df_sell_date['volume']
        df['cum_volume']=df_date['cum_volume']
        df['cum_amount'] = df['cum_volume']*df['close']
        # df.loc[:,['sell_price','sell_volume']]=df_sell_date.loc[:,['price','volume']]
        df.fillna(value=0,inplace=True)

        df['buy_profit']=(df['close']-df['buy_price'])*df['buy_volume']
        df['buy_profit'] = (df['close'] - df['buy_price']) * df['buy_volume']
        df['sell_profit'] = (df['sell_price'] - df['open']) * df['sell_volume']
        df['day_prifit']=(df['cum_volume']-df['buy_volume'])*df['price_change']
        df['profit']=df['buy_profit']+df['sell_profit']+df['day_prifit']
        df['profit_rate']=df['profit']/((df['cum_volume']-df['buy_volume'])*df['close']+df['buy_volume']*df['buy_price']+df['sell_volume']*df['sell_price'])
        df['profit_rate'].fillna(value=0,inplace=True)
        # profit=df['buy_profit'].sum()+df['sell_profit'].sum()+df['day_prifit'].sum()
        # print(profit)
        # print(df)
        # print(df['profit'].sum())
        return df.loc[:,['cum_amount','profit','profit_rate']]
if __name__=="__main__":
    metric=Metric()
    metric.stat(account_id = "back_test20230307175819")
    metric.print_stat()
    # NewMetric().stat()
    # account_id = "back_test20221212163953"
    # # account_id = "back_test20221215141858"
    #divide_symbol_trade_record
    # # df = NewMetric().get_symbol_profit(df_trade)
    #
    # df=NewMetric().get_profit(df_trade)
    # df['cum_prifit']=df['profit'].cumsum()
    # df_benmark = NewMetric().get_benchmark_returns(start_time=df_trade['trade_date'].min(),
    #                                             end_time=df_trade['trade_date'].max(), symbol='SHSE.000001')
    #
    # print(df_benmark)
    # benchmark_returns = df_benmark['change'].values
    # print(df)
    # df_trade = Order().getRecord(account_id="back_test20221220194906")
    # NewMetric().symbol_trade_stat(df_trade.loc[df_trade['symbol']=='SZSE.000858',:])
    # NewMetric().divide_symbol_trade_record(df_trade.loc[df_trade['symbol']=='SHSE.601318',:])
    # profit_rates,profit_rate,profits=NewMetric().close_stat(df_close,df_sell)
    # print(profit_rates,profit_rate,profits)

    # print(df_close)
    # # print(df_unclose)
    # df=NewMetric().rebuild_trade_record(df_close,df_sell)
    # print(df)