import datetime
from quant.trader import Trader

# 策略基类
class StrategyBase():
    # 日内交易已卖出股票代码数组
    sell_symbols = []
    # 日内交易已买入股票代码数组
    buy_symbols = []

    def __init__(self, context, broker, send_order_event_handler=None):
        self.context = context
        # 经纪商
        self.broker = broker
        # 订单回调函数
        self.broker.send_order_event_handler = send_order_event_handler
        # 订单交易对象
        self.trader = Trader(context, broker)
        # 策略名称
        self.strategy_name = ''

        # 策略交易已卖出股票代码数组
        self.strategy_sell_symbols = []
        # 策略交易已买入股票代码数组
        self.strategy_buy_symbols = []
        # self.get_order_symbols()
        # 上次检查资金流时间
        self.money_flow_time = datetime.datetime.strptime(
            "{} {}".format(datetime.datetime.now().strftime("%Y-%m-%d"), "09:30:00"), "%Y-%m-%d %H:%M:%S")

    # # 获取缓存持仓信息
    def get_cache_position(self, positions, symbol):
        ret = None
        for pos in positions:
            if pos.symbol == symbol:
                ret = pos
                break
        return ret

    # 获取订单股票代码
    def get_order_symbols(self):
        for o in self.context.orders:
            # 所有交易代码
            if o.status == 5:
                continue
            if o.side == 1:
                if o.symbol not in self.buy_symbols:
                    self.buy_symbols.append(o.symbol)
            else:
                if o.symbol not in self.sell_symbols:
                    self.sell_symbols.append(o.symbol)

            # 略策交易代码
            if o.strategy == self.strategy_name:
                if o.side == 1:
                    if o.symbol not in self.strategy_buy_symbols:
                        self.strategy_buy_symbols.append(o.symbol)
                else:
                    if o.symbol not in self.strategy_sell_symbols:
                        self.strategy_sell_symbols.append(o.symbol)


#     # 获取股票代码的订单
    def get_symbol_orders(self,symbol,side):
        orders=[]
        for o in self.context.orders:
            if (o.symbol==symbol) and (o.side==side):
                orders.append(o)

        return orders