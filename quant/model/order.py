# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:本地定单类
# Copyright (C) 2021-2023
###############################################################################
#
from datetime import datetime
import datacompy
from quant.util import stringutil
from quant.util.configutil import get_config
from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json

Base = declarative_base()

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)
pd.options.mode.chained_assignment = None

class Order(Base):
    # 指定本类映射到users表
    __tablename__ = 'order'
    __connectString__=get_config('DATABASE','tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)

    account_id = Column(String(50))
    cl_ord_id = Column(String(50))
    symbol = Column(String(20))
    side = Column(Integer)
    price = Column(Float(10))
    volume = Column(Integer)
    amount = Column(Float(10))
    factor = Column(String(50))
    indicator = Column(String(500))
    strategy = Column(String(50))
    status=Column(Integer)
    mode = Column(Integer)
    trade_date=Column(String(20))
    trade_time =Column(DateTime,default=datetime.now())
    record_time = Column(DateTime, default=datetime.now())

    # 插入新记录
    def insert(self):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        # DBSession = sessionmaker(bind=engine)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        # 创建session对象:
        session = DBSession()
        # 添加到session:
        session.add(self)
        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()

    #获取完成交订单
    def get_unfinished_order(self,account_id,date):
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("SELECT a.* FROM `order` a,(SELECT symbol,SUM(volume*side) vol FROM `order`  WHERE account_id='{}' AND trade_time<='{}' group by symbol  HAVING vol>0) b WHERE a.account_id='{}' AND a.symbol=b.symbol AND a.volume=b.vol AND a.side=1 AND a.trade_time<='{}' order BY trade_time desc".format(account_id,date,account_id,date), con=engine)
        df.drop_duplicates(subset=['symbol'],inplace=True)
        engine.dispose()
        return df

    # 获取某天的交易记录
    def getRecord(self,start=None,end=None,account_id='d28f4b30-4bf9-11ec-ad1b-00163e0a4100'):
        engine = create_engine(self.__connectString__)
        where=" `status`=3 "
        if start!=None:
            where="trade_date>='{}'".format(start)
        if end!=None:
            if where!='':
                where=where+' and '
            where=where+"trade_date<='{}'".format(end)
        if account_id!="":
            if where != '':
                where = where + ' and '

            if "'" in account_id:
                account_id=account_id.replace("'","")
            where = where + " account_id='{}'".format(account_id)
        if where!='':
            where=" where {}".format(where)
        df=pd.read_sql("select * from `{}` {}".format(self.__tablename__,where),con=engine)
        engine.dispose()
        return df

    # 获取某天的交易记录
    @classmethod
    def get_day_orders(self,account_id,date):
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        # DBSession = sessionmaker(bind=engine)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        # 创建session对象:
        session = DBSession()
        ret = session.query(Order).filter(Order.account_id == account_id).filter(Order.trade_date == date).all()
        engine.dispose()
        return ret

    # 获取某天的交易记录
    @classmethod
    def get_last_orders(self,account_id,symbols):
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        # DBSession = sessionmaker(bind=engine)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        # 创建session对象:
        session = DBSession()
        query = session.query(Order).filter(Order.account_id == account_id).filter(Order.side == 1).filter(Order.symbol.in_(symbols))
        df = pd.read_sql(query.statement, engine)
        df.sort_values(by='trade_time',ascending=False,inplace=True)
        df.drop_duplicates(subset='symbol',inplace=True)
        engine.dispose()
        return df

    # 获取某天的交易记录
    @classmethod
    def get_day_sellout_orders(self,date,account_id=''):
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        # DBSession = sessionmaker(bind=engine)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        # 创建session对象:
        session = DBSession()
        if account_id=='':
            ret = session.query(Order).filter(Order.side == -1).filter(Order.status == 3).filter(Order.trade_date == date).all()
        else:
            ret = session.query(Order).filter(Order.account_id == account_id).filter(Order.status == 3).filter(Order.side == -1).filter(Order.trade_date == date).all()
        engine.dispose()
        df=pd.DataFrame()
        if len(ret)>0:
            df = self.to_df(ret)
            df.drop_duplicates(subset='symbol',keep='first',inplace=True)
            df.set_index('symbol',inplace=True)
        return df
    # 获取某天的交易记录
    # @classmethod
    # def get_last_order(self):
    #     engine = create_engine(self.__connectString__)
    #     DBSession = sessionmaker(bind=engine, expire_on_commit=False)
    #     session = DBSession()
    #     ret = session.query(Order).filter(Order.trade_date == date).all()
    #     engine.dispose()
    #     return ret

    # 更新订单状态
    @classmethod
    def update_trade_amount(self,cl_ord_id,volume,amount):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        js={"volume": volume,"amount": amount,"status":3}
        # ret = session.query(Position).all()
        # session.query(Order).filter(Order.cl_ord_id == cl_ord_id).first()
        order=session.query(Order).filter(Order.cl_ord_id == cl_ord_id).first()
        if order:
            if order.status!=3:
                 session.query(Order).filter(Order.cl_ord_id == cl_ord_id).update(js)
                # .filter(Order.trade_date == trade_date).filter(Order.cl_ord_id == cl_ord_id).update(js)
        session.commit()
        engine.dispose()

    # 更新订单状态
    @classmethod
    def update_status(self,accountid,trade_date,cl_ord_id,status):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        js={"status": status}
        session.query(Order).filter(Order.account_id == accountid).filter(Order.trade_date == trade_date).filter(Order.cl_ord_id == cl_ord_id).update(js)
        session.commit()
        engine.dispose()

    #对象转json
    def to_json(self):
        js = {'account_id': self.account_id,'cl_ord_id': self.cl_ord_id,'symbol': self.symbol ,'side': self.side,'price': self.price ,
              'volume': self.volume ,'amount': self.amount ,'factor': self.factor ,'strategy': self.strategy,'status': self.status,'mode': self.mode,'trade_date': self.trade_date, 'trade_time': self.trade_time, 'record_time': self.record_time }
        return js

    # 反序列化
    def from_json(self,js):
        order=json.loads(js)
        return order

    # 对象数组转dataframe
    @classmethod
    def to_df(self,pos):
        df=None
        if len(pos)>0:
            df=pd.DataFrame(pos[0].to_json(),index=[0])
            for i in range(len(pos)):
                if i>0:
                    df=df.append(pd.DataFrame(pos[i].to_json(),index=[i]))
            # df['symbol']=df['code'].apply(lambda x:stockutil.xtToGmSymbol(x))
        return df




    # 本地订单数据和掘金终端回测订单数据一致性比较
    def compare_myquant_backtest_order(self,account_id='back_test20221020180110',file="E:\\backtest\\aa.csv"):
        orders = self.getRecord(account_id=account_id)
        # # orders = Order().get_day_orders('2018-06-05')
        orders = orders.loc[:, ['symbol', 'side', 'status', 'volume', 'amount', 'trade_date']]
        # print(orders)
        df = pd.read_csv(file)
        df['trade_date'] = df['createdAt'].apply(lambda x: x[0:10])
        df['side'] = df['side'].apply(lambda x: x if x == 1 else -1)
        df['amount'] = round(df['value'], 1)
        df = df.loc[:, ['symbol', 'side', 'status', 'volume', 'amount', 'trade_date']]

        # print(df)

        compy = datacompy.Compare(orders, df, on_index=True)

        print(compy.matches())
        print(compy.report())

    # 获取某天交易记录
    def get_day_trade_record(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',date=datetime.now().strftime('%Y-%m-%d')):
        engine = create_engine(self.__connectString__)
        df_sellout = pd.read_sql("SELECT * FROM `order` WHERE account_id='{}' and trade_date='{}';".format(account_id,date), con=engine)
        return df_sellout

    def get_day_sellout_stock(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',date=datetime.now().strftime('%Y-%m-%d')):
        engine = create_engine(self.__connectString__)
        df_sellout = pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) as volume  FROM `myorder` WHERE STATUS=3 AND account_id='{}' AND symbol IN (SELECT symbol FROM myorder WHERE STATUS=3 AND side=-1 AND account_id='{}' AND trade_date='{}') GROUP BY symbol HAVING volume=0 order BY volume;".format(account_id,account_id,date), con=engine)
        return df_sellout

    # 每天清仓股票统计
    def get_day_sellout_profit(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',date=datetime.now().strftime('%Y-%m-%d')):
        df_sellout = self.get_day_sellout_stock(account_id=account_id, date=date)
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("SELECT * FROM `order` WHERE STATUS=3 AND account_id='{}' AND trade_date<='{}'".format(account_id, date), con=engine)
        symbols=stringutil.array_to_string(df_sellout['symbol'].values)
        symbols="'{}'".format(symbols.replace(',',"','"))
        df_sell=pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) as volume  FROM `order` WHERE STATUS=3 AND side=-1 AND account_id='{}' AND symbol IN ({}) AND trade_date='{}' GROUP BY symbol order BY volume;".format(account_id,symbols, date), con=engine)
        engine.dispose()

        df_out = df.loc[df.symbol.isin(df_sellout.symbol) & (df['side'] == 1), :].copy()
        df_ret = pd.DataFrame(columns=df_out.columns)

        df_ret=pd.concat([df_ret,df.loc[(df['trade_date']== date) & (df['side'] == -1) & (df['symbol'].isin(df_sell['symbol'])), :].copy()],axis=0,ignore_index=True)

        df_sell.set_index('symbol', inplace=True)

        for i,row in df_sellout.iterrows():
            df_symbol=df_out.loc[(df_out['symbol']==row['symbol']) ,:].copy()
            df_symbol.sort_values(by='trade_time', ascending=False,inplace=True)
            df_symbol['volume_cumsum']=df_symbol['volume'].cumsum()

            df_ret=pd.concat([df_ret,df_symbol.loc[df_symbol['volume_cumsum']<=-df_sell.at[row['symbol'],'volume'],:].copy()],axis=0,ignore_index=True)

        return df_ret

        # 获取已清仓股票盈利统计
    def get_close_profit(self,start,end,account):
        df_trade=self.getRecord(start,end,account)
        df_trade['trade']=df_trade['volume']*df_trade['side']
        df_trade['trade_amount'] = df_trade['amount'] * df_trade['side']*-1
        df= df_trade.groupby(['symbol']).sum(['trade','trade_amount'])
        # xx=map(lambda x: x.split('.')[1], df.index)
        # df['code'] = df.index
        # df['code']=df['code'].apply(lambda x: x.split('.')[1])
        # # df['code']=df.index.apply(lambda x:stockutil.delSymbolPrefix(x))
        # df_name=StockInfo().get_stock_by_symbols(df.index)
        # df['name']=df_name['name']
        df['name'] = ''
        if len(df)>0:
            df=df.loc[df['trade']==0,:]
        return df

        # 获取已清仓股票盈利统计
    def get_stock_profit(self,start,end,account):
        df_trade=self.getRecord(start,end,account)
        df_trade['trade']=df_trade['volume']*df_trade['side']
        df_trade['trade_amount'] = df_trade['amount'] * df_trade['side']*-1
        df= df_trade.groupby(['symbol']).sum(['trade','trade_amount'])
        # xx=map(lambda x: x.split('.')[1], df.index)
        # df['code'] = df.index
        # df['code']=df['code'].apply(lambda x: x.split('.')[1])
        # # df['code']=df.index.apply(lambda x:stockutil.delSymbolPrefix(x))
        # df_name=StockInfo().get_stock_by_symbols(df.index)
        # df['name']=df_name['name']
        df['name']=''
        df_finished=None
        df_unfinished=None
        if len(df)>0:
            df_finished=df.loc[df['trade']==0,:]
            df_unfinished = df.loc[df['trade'] != 0, :]
        return (df_finished,df_unfinished)

    # 删除代码列数据
    def get_order_by_symbols(self,symbols=[],account_id=None):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        query = session.query(Order).filter(Order.account_id==account_id).filter(Order.symbol.in_(symbols))
        df = pd.read_sql(query.statement, engine)
        session.commit()
        engine.dispose()
        return df

    # 获取订单买入策略
    def get_symbols_strategy(self,account_id,symbols=[]):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        query = session.query(Order).filter(Order.account_id==account_id).filter(Order.symbol.in_(symbols))
        df = pd.read_sql(query.statement, engine)
        session.commit()
        engine.dispose()
        df.sort_values(by='trade_time')
        df.drop_duplicates(subset=['symbol'],keep='last',inplace=True)
        df.set_index('symbol',inplace=True)
        df=df.loc[:,['strategy']]
        return df

    # 获取单个股票交易记录
    def getTradeRecord(self,symbol,acount,start=None,end=None):
        engine = create_engine(self.__connectString__)
        if "'" in acount:
            acount=acount.replace("'","")
        where=" symbol='{}' and account_id='{}'".format(symbol,acount)
        if start!=None:
            where=where+" and trade_time>='{}'".format(start)
        if end!=None:
            where=where+" and trade_time<='{}'".format(end)
        if where!='':
            where=' where {}'.format(where)
        df=pd.read_sql("select * from `{}` {}".format(self.__tablename__,where),con=engine)
        engine.dispose()
        df_buy=df.loc[df['side']==1,:]
        df_buy=df_buy.groupby(['trade_date']).sum(['amount', 'volume'])
        df_buy['buy']=round((df_buy['amount']/df_buy['volume']),2)

        df_sell = df.loc[df['side'] == -1, :]
        df_sell = df_sell.groupby(['trade_date']).sum(['amount', 'volume'])
        df_sell['sell'] = round((df_sell['amount'] / df_sell['volume']), 2)
        df_trade = df.groupby(['trade_date']).sum(['amount', 'volume'])
        df_trade['buy']=df_buy['buy']
        df_trade['sell'] = df_sell['sell']
        df_trade.index=pd.to_datetime(df_trade.index)
        # print(df_trade)
        return df_trade

    # 获取单个股票交易记录
    def getAccount(self):
        engine = create_engine(self.__connectString__)
        # where=" "
        # if start!=None:
        #     where=where+" trade_time>='{}'".format(start)
        # if end!=None:
        #     where=where+" and trade_time<='{}'".format(end)
        # if where!='':
        #     where=' where {}'.format(where)
        # df=pd.read_sql("SELECT account_id,COUNT(*) AS cnt FROM trade_record GROUP BY account_id {}".format(where),con=engine)
        df = pd.read_sql("SELECT account_id,COUNT(*) AS cnt FROM `{}` GROUP BY account_id ".format(self.__tablename__),
                         con=engine)
        engine.dispose()
        return df
    # 获取最多交易记录帐号
    def getAccountId(self):
        ret=''
        df=self.getAccount()
        if len(df)>0:
            df.sort_values(by=['cnt'],ascending=False,inplace=True)
            ret=df.at[0,'account_id']
        return ret

    def get_order(self,id):
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        # DBSession = sessionmaker(bind=engine)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        # 创建session对象:
        session = DBSession()
        ret = session.query(Order).filter(Order.id == id).first()
        engine.dispose()
        return ret
if __name__=='__main__':
    df=Order().get_last_orders('5726b94f-51b3-11ed-b7d9-00163e12c161',['SZSE.002841','SHSE.600585'])
    print(df)
    # Order().compare_myquant_backtest_order(account_id='back_test20221220170017',file='E:\\backtest\\交易明细-268691ae-0401-11ed-81ea-5811220c517b.csv')

    # {'volume': 38100.0, 'amount': 479050.9998, 'status': 3, 'cl_ord_id_1': 'f586538f-5f06-11ed-ba76-00e04ca2738c'}]
    # ord=Order().get_close_profit(start='2021-11-08',end='2022-11-08',account='back_test20221110175717')
    # b= Order().get_symbols_strategy('back_test20221206111043',['SHSE.600089','SHSE.601628','SHSE.600426'])
    # print(b)
    # order = Order().update_trade_amount(cl_ord_id='ca4a3252-5b1c-11ed-bd20-5811220c517b',amount=44.0,volume=44)
    # order.account_id = "account_id"
    # order.symbol = "symbol"
    # order.side = 1
    # order.price = 1
    # order.volume = 1
    # order.factor = "factor"
    # order.strategy = "strategy"
    # order.date = datetime.datetime.now().strftime('%Y-%m-%d')
    # order.update_date = datetime.datetime.now()
    # order.status = 0
    # order.insert()
    # orders= Order().getRecord(acount='back_test20221107153118')
    # orders=orders.loc[:,['symbol','side','price','trade_date']]
    # orders.set_index('trade_date', inplace=True,drop=True)
    # orders.to_csv("e:\\orders.csv")
    # print(orders)
    # # # # orders = Order().get_day_orders('2018-06-05')
    # # orders=orders.loc[:,['symbol','side','status','volume','amount','trade_date']]
    # # print(orders)
    # df=pd.read_csv("E:\\c1.csv")
    # df=df.loc[:,['symbol','side','price','trade_date']]
    # df.set_index('trade_date', inplace=True,drop=True)
    # df.to_csv("e:\\df.csv")
    # print(df)
    # # # df['trade_date']=pd.to_datetime(df['createdAt']).strftime("Y%-m%-d%")
    # # df['trade_date'] = df['createdAt'].apply(lambda x: x[0:10])
    # # df['side'] = df['side'].apply(lambda x: x if x==1 else -1)
    # # df['amount'] =round(df['value'],1)
    # # df=df.loc[:,['symbol','side','status','volume','amount','trade_date']]
    # #
    # # print(df)
    # #
    # compy = datacompy.Compare(orders, df, on_index=True)
    # #
    # print(compy.matches())
    # print(compy.report())
    #
    # orders = Order().get_unfinished_order(account_id='back_test20221104210031',date='2018-02-28')
    # print(orders['symbol'])