import datetime
from decimal import Decimal
import pandas as pd
from gm.api import *
from quant.brokers.myquantbroker import MyquantBroker
from quant.account import Account
from quant.api.gmapi import GmApi
from quant.enums.brokers import Brokers
from quant.enums.ratings import Ratings
from quant.indicators import Indicator
from quant.logger import Logger
from quant.model.backtestrecord import BacktestRecord
from quant.model.executionreport import ExecutionReport
from quant.model.myorder import MyOrder
from quant.model.order import Order
from quant.model.position import Position
from quant.model.setting import Setting
from quant.model.stockindicator import StockIndicator
from quant.picker import Picker
from quant.stockdata import StockData
from quant.strategyengine import StrategyEngine
from quant.trader import Trader
from quant.util import stockutil, pdutil, globalvars
from quant.util.datetimeutil import get_pass_minutes
from quant.util.pdutil import get_obj_from_df

class QuantEngine(Context):
    """ 策略基类"""
    def __init__(self,context):
        # 订阅浦发银行, bar频率为一天和一分钟
        # 订阅订阅多个频率的数据，可多次调用subscribe
        self.context=context
        # 获取当前setting帐号id
        if len(context.accounts)==0:
            Logger().loginfo("当然设置的帐号交易配置文件错误:略策文件没有挂接交易帐号")
            stop()

        #     获取交易帐号设置参数
        setting_account_id=Setting.get_setting_accountid(context)
        setting = Setting().getdata(setting_account_id)
        if setting==None:
            Logger().loginfo("当然设置的帐号：{}，交易配置文件错误：数据库setting表没有配置交易设置信息".format(context.setting_account_id))
            stop()
        else:
            context.setting=setting

        # 设置当然帐号对象
        self.account=Account(self.context)
        if context.mode==MODE_BACKTEST:
            self.account.account_id=self.context.backtest_account_id
        # 显示输出交易帐号设置参数
        self.account.display_run_param()

        # bars存贮对象
        self.bars=pd.DataFrame(columns=['symbol','eob','bob','open','close','high', 'low', 'volume', 'amount', 'pre_close','position','frequency', 'receive_local_time'])

        # 持仓股票
        context.holding_symbols=[]
        # 订阅全部代码数组
        context.all_symbols=[]
        # 停牌股票代码
        self.suspension_symbols=[]
        # 设定经纪商
        self.broker=self.get_borker(context=context,broker_type=setting.broker)
        # 初始化交易类
        self.trader=Trader(context,self.broker)
        #交易执行因子
        # self.tradefactor=dict()

        # 打印显示当前帐号资金信息
        self.broker.display_account_asset_info()

        # 获取持仓信息并打印输出
        context.positions=self.broker.getPositions(display=True)

        # 持仓代码数组
        context.holding_symbols.clear()
        if len(context.positions) > 0:
            for i in range(len(context.positions)):
                if context.positions[i].volume>0:
                    context.holding_symbols.append(context.positions[i].symbol)
                    context.all_symbols.append(context.positions[i].symbol)

        if len(context.holding_symbols)>0:
            Logger().loginfo("当前持仓股票：{}".format(context.holding_symbols))
        else:
            message="-------------------当前没有持仓或者帐号设置错误---------------------"
            Logger().loginfo(message)

        # 设置交易标的代码
        codes=['002841','600050']
        # codes=[]
        context.df_buy_stock=Picker().get_picktime(context=context,codes=codes)
        # 择时交易标的股票代码数组
        context.buy_symbols=[]
        for i,row in context.df_buy_stock.iterrows():
            context.buy_symbols.append(stockutil.getGmSymbol(row.code))
            context.all_symbols.append(stockutil.getGmSymbol(row.code))

        if len(context.buy_symbols)>0:
            Logger().loginfo("择时交易标的股票代码：{}".format(context.buy_symbols))
            Logger().loginfo(context.df_buy_stock.loc[:,['code','name']])
        else:
            message="--------------------picktime股票列表为空----------------------------"
            Logger().loginfo(message)

        # 当前交易日期，只对回测有用
        self.day=context.now.day

        # 初始化交易策略
        # 当天交易订单数组
        context.orders = Order.get_day_orders(self.account.get_account_id(),context.now.strftime("%Y-%m-%d"))
        context.last_orders = Order.get_last_orders(self.account.get_account_id(), context.holding_symbols)

        # 策略引擎初始化，同时初始化所有策略
        # strategy_list=Strategy().get_strategy(self.account.account_id)
        strategy_list=[]
        if globalvars.hand_trade=='1':
            # 手工交易
            strategy_list =['SubjectivityStrategy']
            self.strategyengine= StrategyEngine(context=context,strategy_list=strategy_list,broker=self.broker,send_order_event_handler=self.on_order_send)
            self.strategyengine.run_schedule()
        else:
            # 程序化交易
            strategy_list = ['GridStrategy']
            strategy_list.extend(context.df_buy_stock['strategy'].drop_duplicates().values)

           #     订阅行情数据
            if len(context.all_symbols) > 0:
                subscribe(symbols=context.all_symbols, frequency='tick', count=1)
                subscribe(symbols=context.all_symbols, frequency='60s', count=1)
            else:
                message = "--------------------当前持仓和择时交易标的股票代码列表均为空，无交易对象，请检查确认，交易终止----------------------------"
                Logger().loginfo(message)
                stop()

            #     更新交易标的指示及相关参数信息，例如kdj等
            self.df_stock = StockData.update_indicator(acount_id=self.account.account_id,
                                                       buy_symbols=context.buy_symbols,
                                                       positions=context.positions, date=context.now)
            for s in self.df_stock['strategy'].values:
                if s not in strategy_list and s!='':
                    strategy_list.append(s)
            # ['MeanRevertingStrategy', 'RiskStrategy', 'TrendFollowingStrategy', 'DayTradingStrategy' ]
            # 策略引擎初始化
            self.strategyengine= StrategyEngine(context=context,strategy_list=strategy_list,broker=self.broker,send_order_event_handler=self.on_order_send)

            # 设置定时任务
            #schedule(schedule_func=, date_rule='1d', time_rule='09:31:00')
            schedule(schedule_func=self.update_position(self.account.account_id,self.broker), date_rule='1d', time_rule='15:40:00')

        #交易标的指示及相关参数对象 stock_indicator数组
        self.stock_indicators=dict()
        # 上证昨日收盘价
        context.sh_index_pre_close=GmApi().get_sh_index_pre_close(context.now)
        # 沪指实时涨跌值百份点
        context.sh_index_change =0
    # 运行定时任务
    def run_schedule(self):
        self.strategyengine.run_schedule()

    # 接收tick事件晌应
    def on_tick(self,context, tick):
        # print(tick)
        # tick数据异常终止执行策略
        if tick.price==0:
            return
        # 只在开盘时间运行
        time_now = context.now.strftime('%H:%M')
        if (time_now>="09:30") & (time_now<="15:30"):
            # 第二个bar之后运行
            if len(self.bars)>0:
                symbol=tick['symbol']
                if symbol in self.stock_indicators.keys():
                    stock_indicator=self.stock_indicators[symbol]
                    # 运行tick驱动的策略
                    # self.strategyengine.run(context=context, stock_indicator=stock_indicator, tick=tick)

    # 接收bar事件晌应
    def on_bar(self,context,bars):
        # 实盘模式接收第一个bar时，补齐交易盘前数据
        if bars[0]['symbol']=='SHSE.000001':
            context.sh_index_change=round(((bars[0]['close']-context.sh_index_pre_close)/context.sh_index_pre_close)*100,2)
            print("沪指{}：{}".format(context.now,context.sh_index_change))
            return
        if (len(self.bars)==0) & (context.mode== MODE_LIVE):
            df_pre=GmApi().get_pre_open_bar(symbol=context.all_symbols,date=context.now.strftime("%Y-%m-%d"))
            self.bars=pd.concat([self.bars,df_pre],axis=0,ignore_index=True)

        # 回测模式，新的一天，重置参数
        if context.mode==MODE_BACKTEST:
            if context.now.day!=self.day:
                # 获取上日沪指指数
                context.sh_index_pre_close = GmApi().get_sh_index_pre_close(context.now)
                context.sh_index_change =0
                # 重置变量的值
                self.suspension_symbols = []
                self.bars.drop(self.bars.index, inplace=True)
                self.day=context.now.day
                Logger().loginfo(context.now.strftime("%Y-%m-%d"))
                # 记录当前回测日期
                BacktestRecord().update_backtest_record(account_id= self.context.backtest_account_id,date=context.now.strftime("%Y-%m-%d %H:%M:%S"),status="suspend")
                context.positions = self.broker.getPositions(display=True)
                # 持仓代码数组
                context.holding_symbols.clear()
                if len(context.positions) > 0:
                    for i in range(len(context.positions)):
                        # if self.positions[i].symbol!='SHSE.600616' and self.positions[i].symbol!='SZSE.002230':
                        if context.positions[i].volume > 0:
                            context.holding_symbols.append(context.positions[i].symbol)
                            context.all_symbols.append(context.positions[i].symbol)
                print(context.holding_symbols)
                # context.orders = Order.get_day_orders(self.account.get_account_id(), context.now.strftime("%Y-%m-%d"))
                context.last_orders = Order.get_last_orders(self.account.get_account_id(), context.holding_symbols)
                self.context.orders=[]

                #     更新交易标的指示及相关参数信息，例如kdj等
                self.df_stock = StockData.update_indicator(acount_id=self.account.account_id, buy_symbols=context.buy_symbols,positions=context.positions, date=context.now)

                # 去掉停牌股票代码
                # for index, row in self.df_stock.iterrows():
                #     if row['suspension'] == True:
                #         self.suspension_symbols.append(row['symbol'])
                #回测时，更新订单中的股票代码
                self.strategyengine.update_order_symbols()

    # 自定义订单发送事件回调，同步订阅股票代码
    def on_order_send(self,order):

        # 如果是回测模块，订单状态直接设为3
        if (self.context.mode == MODE_BACKTEST):
            order.status=3

        self.context.orders.append(order)

        # # 更新持仓股票可用数
        # if order.side == "-1":
        #     for i in range(len(self.context.positions)):
        #         if self.context.positions[i].symbol==order.symbol:
        #             self.context.positions[i].volume=self.context.positions[i].volume-order.volume
        #             self.context.positions[i].can_use_volume=self.context.positions[i].can_use_volume-order.volume
        #             break

        # print(Position.to_df(self.context.positions))
        # print(Order.to_df(self.context.orders))
        pass

    # 掘金订单状态事件回调，同步持仓股票
    def on_order_status(self,context, order):
        Logger().loginfo("on_order_status:{}".format(datetime.datetime.now()))
        # 更新内存订单信息
        if self.context.mode==MODE_LIVE:
            self.update_memory_orders(order.cl_ord_id,order.status)
            Order.update_status(order.account_id,str(order.updated_at)[0:10], order.cl_ord_id, order.status)
        # context.positions=self.broker.getPositions(display=True)
        if order.order_id:
            myorder=MyOrder()
            myorder.mode=self.context.mode
            myorder.order_id=order.order_id
            myorder.account_id = order.account_id
            myorder.cl_ord_id = order.cl_ord_id
            myorder.symbol = order.symbol
            myorder.status = order.status
            if order.side==2:
                myorder.side=-1
            else:
                myorder.side = order.side

            myorder.volume = order.volume
            myorder.price = order.price
            myorder.value = order.value
            myorder.amount = order.filled_amount
            myorder.created_at = order.created_at
            myorder.updated_at = order.updated_at
            myorder.cl_ord_id = order.cl_ord_id
            myorder.ex_ord_id = order.ex_ord_id
            myorder.trade_date =  datetime.datetime.now().strftime("%Y-%m-%d")
            myorder.trade_time = order.created_at
            myorder.record_time = datetime.datetime.now()
            myorder.save()

            # # 直接更新订单状态，如果是实盘模式
            # if (context.mode == MODE_LIVE):
            #     Order.update_status(myorder.cl_ord_id, myorder.status)
        # if (order.OrderStatus==OrderStatus_PartiallyFilled) | (order.OrderStatus==OrderStatus_Filled):
        # GmApi().update_execution_reports()


    #掘金订单状态事件回调，同步持仓股票
    def on_execution_report(self,context, execrpt):

        Logger().loginfo("on_execution_report:{}".format(datetime.datetime.now()))

        if execrpt != None:
            if execrpt.exec_type == 15:
                execute_report = ExecutionReport()
                execute_report.mode=context.mode
                if (context.mode == MODE_BACKTEST):
                    # trade_record.account_id ="{}{}".format(context.setting.account_id,context.backtest_id)
                    # trade_record.account_id=context.backtest_id
                    execute_report.account_id=self.account.get_account_id()
                else:
                    execute_report.account_id=execrpt.account_id

                execute_report.cl_ord_id= execrpt.cl_ord_id
                execute_report.symbol = execrpt.symbol

                if execrpt.side==1:
                    execute_report.side = 1
                elif execrpt.side==2:
                    execute_report.side=-1
                execute_report.price = execrpt.price
                execute_report.volume = execrpt.volume
                execute_report.trade_date= execrpt.created_at.strftime('%Y-%m-%d')
                execute_report.amount =Decimal(execrpt.amount).quantize(Decimal('0.00'))
                execute_report.trade_time=pd.to_datetime(execrpt.created_at).strftime('%Y-%m-%d %H:%M:%S')

                if execrpt.symbol in self.trader.trade_records.keys():
                    execute_report.strategy= self.trader.trade_records[execrpt.symbol]

                execute_report.record_time = datetime.datetime.now()
                # 直接更新订单状态，如果是回测模式
                # if (context.mode == MODE_BACKTEST):
                #     Order.update_status(accountid=execute_report.account_id,trade_date=execute_report.trade_date,cl_ord_id=execute_report.cl_ord_id,status=3)

                # 如果没有存在
                if ExecutionReport().hasExistTradeRecord(execute_report.symbol,execute_report.trade_time,execute_report.amount)==False:
                    try:
                        execute_report.insert()
                    except Exception as e:
                        Logger().logerror('交易记录保存错误：{}'.format(e))
                unsubscribe(symbols=execrpt.symbol, frequency='tick')

    #获取经纪商
    def get_borker(self,context,broker_type):
        if broker_type==Brokers.xtquant.value:
            # broker=XtBroker(context=context)
            pass
        else:
            broker = MyquantBroker(context=context)
        return broker

    # 获取持仓策略

    # 更新持仓
    @classmethod
    def update_position(self,account_id,broker):
        StockData.update_position(broker)

   # 更新持仓
   #  @classmethod
    def update_memory_orders(self,cl_ord_id,status):
        for i in range(len(self.context.orders)):
            if self.context.orders[i].cl_ord_id==cl_ord_id:
                order=self.context.orders[i]
                del self.context.orders[i]
                order.status=status
                self.context.orders.append(order)

        Logger().loginfo(Order.to_df(self.context.orders))

if __name__=='__main__':

    pass
