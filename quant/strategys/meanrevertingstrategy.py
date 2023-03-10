from quant.enums.strategytype import StrategyType
from quant.logger import Logger
from quant.model.position import Position
from quant.signalengine import SignalEngine
from quant.strategys.strategybase import StrategyBase

# 均值回归策略
class MeanRevertingStrategy(StrategyBase):
    def __init__(self,context,broker,send_order_event_handler=None):
        super().__init__(context,broker,send_order_event_handler)
        # 策略名称
        self.strategy_name = 'MeanRevertingStrategy'
        # 行情推送数据类型bar,tick
        self.drive_type=StrategyType.bar.value
        # 获取当天已交易订单信息
        self.get_order_symbols()
        #日内交易已卖出股票代码数组
        self.meanreverting_sell_symbols=self.strategy_sell_symbols
        # 日内交易已买入股票代码数组
        self.meanreverting_buy_symbols=self.strategy_buy_symbols
        # signal_list = ['MtmSignal', 'KdjSignal']
        signal_list=['KdjSignal']
        self.signals=SignalEngine(signal_list)
    # 执行买入操作
    def do_buy(self, context, bar, stock_indicator):
        # k_pre, d_pre, j_pre, k, d, j
        symbol=bar['symbol']
        price=bar['close']
        if (symbol in context.buy_symbols) and (symbol not in context.holding_symbols) :

            fit_signal=self.signals.fit_buy(stock_indicator)
            if fit_signal[0]:
                factor =fit_signal[1]
                indicator = fit_signal[2]

                # if self.fit_money_flow(stock_indicator=stock_indicator):
                if symbol not in StrategyBase.buy_symbols:
                    print("------------------buy-------------------")
                    StrategyBase.buy_symbols.append(symbol)
                    self.trader.buy(symbol=symbol,price= bar['close'],factor= factor,strategy=self.strategy_name,indicator=indicator)

    # 执行卖出操作
    def do_sell(self, context, bar,stock_indicator):
        symbol = bar['symbol']
        if symbol in context.holding_symbols:
            pos = Position().get_cache_position(context.positions, symbol)
            if pos:
                if (pos.can_use_volume>0):
                    price = bar['close']
                    fit_signal = self.signals.fit_sell(stock_indicator)
                    if fit_signal[0]:
                        factor = fit_signal[1]
                        indicator = fit_signal[2]
                        if symbol not in StrategyBase.sell_symbols:
                            print("------------------sell-------------------")
                            StrategyBase.sell_symbols.append(symbol)
                            self.trader.sell_out(symbol,price,factor=factor,strategy=self.strategy_name,indicator=indicator)

    def run(self,context,bar,stock_indicator):
        Logger().logdebug('正在运行策略：{}'.format(self.strategy_name))
        symbol=bar['symbol']
        # self.fit_money_flow(stock_indicator)
        if symbol in context.holding_symbols:
            self.do_sell(context,bar,stock_indicator)

        if symbol in context.buy_symbols:
            self.do_buy(context, bar, stock_indicator)

    #更新当天订单股票代码
    def update_order_symbols(self):
        # 获取当天已交易订单信息
        self.get_order_symbols()
        # # 日内交易已卖出股票代码数组
        StrategyBase.sell_symbols= []
        # # 日内交易已买入股票代码数组
        StrategyBase.buy_symbols= []
        # 日内交易已卖出股票代码数组
        self.meanreverting_sell_symbols = []
        # 日内交易已买入股票代码数组
        self.meanreverting_buy_symbols = []