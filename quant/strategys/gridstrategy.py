from quant.enums.scopes import Scopes
from quant.enums.strategytype import StrategyType
from quant.logger import Logger
from quant.model.position import Position
from quant.strategys.strategybase import StrategyBase
from quant.util import stockutil

# 网格交易策略
class GridStrategy(StrategyBase):

    def __init__(self,context,broker,send_order_event_handler=None):
        # 初始化父类
        super().__init__(context,broker,send_order_event_handler)
        # 策略名称
        self.strategy_name='GridStrategy'
        # 行情推送数据类型bar,tick
        self.drive_type = StrategyType.bar.value
        self.scope = Scopes.universal
        # 获取当天已交易订单信息
        self.get_order_symbols()
        #日内交易已卖出股票代码数组
        self.daytrading_sell_symbols=self.strategy_sell_symbols
        # 日内交易已买入股票代码数组
        self.daytrading_buy_symbols=self.strategy_buy_symbols
        # 偏离分时均价阀值
        self.threshold=0.02
        # 日内交易截止时间
        self.daytradeing_time="14:55"

    # 从最后买单中找出当前股票的订单
    def get_last_order(self, context,symbol):
        return context.last_orders[context.last_orders['symbol']==symbol]

    # context.last_orders.at[context.last_orders[context.last_orders['symbol'] == symbol].index[0], 'price'
    # 执行买入操作
    def do_buy(self, context, tick, stock_indicator):
        # ma_price=stock_indicator.map
        symbol=tick['symbol']
        price=tick['close']
        factor = ""
        time_now = context.now.strftime('%H:%M')

        df=self.get_last_order(context,symbol)
        if len(df)==0:
            return
        last_price=df.at[df.index[0], 'price']
        # 如果在日内交易时间设置前，则进行日内交易
        if (time_now <self.daytradeing_time):
            # m_kdj=stock_indicator.minute_kdj
            # # print(m_kdj)
            # if ((m_kdj[0]<m_kdj[1]) and (m_kdj[3]>=m_kdj[4])):
            if (last_price-price)/last_price > self.threshold :
                factor = "fit_buy_gridstrategy"

        # 如果在日内交易时间设置后，如果有卖出交易，格价在分时均线之后，买回
        else:
            # if (symbol in context.daytrading_sell_symbols) and (symbol not in context.daytrading_buy_symbols):
            #     factor="DayTradingStrategy_buy"
            pass
        if factor!="":

            if symbol not in self.daytrading_buy_symbols:
                print("------------------buy-------------------")
                self.daytrading_buy_symbols.append(symbol)
                self.trader.buy(symbol= symbol,price= price,factor= factor,strategy=self.strategy_name)

    # 执行卖出操作
    def do_sell(self,context,tick,stock_indicator):
        # ma_price=stock_indicator.map
        symbol = tick['symbol']
        price = tick['close']
        if (symbol not in context.holding_symbols):
            return


        pos=Position().get_cache_position(context.positions,symbol)
        # print(obj_to_series(pos))
        # 如果没有持仓，则终止
        if pos.can_use_volume==0:
            return

        volume=stockutil.value_to_volume(context.setting.per_buy_amount,price)

        if volume>pos.can_use_volume:
            volume=pos.can_use_volume
        factor=""

        # 如果在日内交易时间设置前，则进行日内交易
        time_now = context.now.strftime('%H:%M')
        df=self.get_last_order(context,symbol)
        if len(df)==0:
            return
        last_price=df.at[df.index[0], 'price']
        if (time_now <self.daytradeing_time):
            if (price-last_price) / last_price > self.threshold and (symbol not in self.daytrading_sell_symbols):
                    factor = "GridStrategy_sell"
        # 如果在日内交易时间设置后，如果有买入交易，格价在分时均线之上，卖出
        # elif (symbol in self.daytrading_buy_symbols) and (symbol not in self.daytrading_sell_symbols):
        #         order=self.get_symbol_orders(symbol,1)
        #         if order[0].price<price*0.99:
        #             factor = "DayTradingStrategy_sell"
        if factor!="":

            if symbol not in self.daytrading_sell_symbols:
                print("------------------sell-------------------")
                self.daytrading_sell_symbols.append(symbol)
                self.trader.sell(symbol= symbol,price= price,volume=volume,factor= factor,strategy=self.strategy_name)

    # def run(self,context,tick,df,**kwargs):
    def run(self,context,bar,stock_indicator):
        tick=bar
        if (stock_indicator.strategy!=self.strategy_name) and (self.scope==Scopes.stock):
            Logger().logdebug('当前股票与当正在运行策略不匹配：{},{}'.format(self.strategy_name,stock_indicator.strategy))
            return
        Logger().logdebug('正在运行策略：{}'.format(self.strategy_name))
        symbol=tick['symbol']
        price=bar['close']

        # pass
        # df=df.loc[df['symbol']==symbol,:]
        # # len(bar)<1
        # if len(df) < 1:
        #     return
        #
        # ma_price=df.iloc[-1].at[DfColumns.curmean.value]
        # 如果没有持仓则不进行日内交易
        # if symbol not in context.holding_symbols:
        #     return
        # 送是否已买入操作
        # if symbol not in self.daytrading_buy_symbols:
        #     self.do_buy(context,tick,stock_indicator.map)
        #
        # if symbol not in self.daytrading_sell_symbols:
        #     self.do_sell(context,tick,stock_indicator.map)

        if symbol not in self.daytrading_buy_symbols:
            # if stock_indicator.stock_type==Ratings.Holding.value:
            self.do_buy(context, tick, stock_indicator)
                    # if stock_indicator.symbol in context.holding_symbols:
                    #     if price < stock_indicator.open_price:
                    #         self.do_buy(context,tick,stock_indicator)
                    # else:
                    #     self.do_buy(context, tick, stock_indicator)
            #         日内卖出

        if (symbol in context.holding_symbols) and (symbol not in self.daytrading_sell_symbols):
            self.do_sell(context,tick,stock_indicator)

    #更新当天订单股票代码
    def update_order_symbols(self):
        # 获取当天已交易订单信息
        self.get_order_symbols()
        # # 日内交易已卖出股票代码数组
        StrategyBase.sell_symbols= []
        # # 日内交易已买入股票代码数组
        StrategyBase.buy_symbols= []
        # 日内交易已卖出股票代码数组
        self.daytrading_buy_symbols = []
        # 日内交易已买入股票代码数组
        self.daytrading_sell_symbols = []