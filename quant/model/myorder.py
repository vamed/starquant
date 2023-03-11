# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:掘金订单类
# Copyright (C) 2021-2023
###############################################################################
#
from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

from quant.util import stringutil
from quant.util.configutil import get_config

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class MyOrder(Base):
    # 指定本类映射到users表
    __tablename__ = 'myorder'
    __connectString__=get_config('DATABASE','tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    account_id = Column(String(50))
    symbol = Column(String(20))
    side = Column(Integer)
    price = Column(Float(10))
    volume = Column(Integer)
    amount = Column(Float(20))
    strategy=Column(String(50))
    trade_date = Column(String(50))
    trade_time = Column(DateTime,default=datetime.now())
    record_time= Column(DateTime,default=datetime.now())
    status = Column(Integer)
    mode = Column(Integer)
    cl_ord_id = Column(String(50))
    order_id = Column(String(50))
    ex_ord_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def tojson(self):
        js = {'account_id': self.account_id, 'symbol': self.symbol,
              'side': self.side,'price': self.price,'volume': self.volume,'amount': self.amount,'strategy': self.strategy,'trade_date': self.trade_date
              ,'trade_time': self.trade_time,'record_time': self.record_time,'status': self.status,'cl_ord_id': self.cl_ord_id,'order_id': self.order_id
              ,'ex_ord_id': self.ex_ord_id,'created_at': self.created_at,'updated_at': self.updated_at}
        return js

    # 获取股票dataframe
    def getdata(self,order_id):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        order = session.query(MyOrder).filter(MyOrder.order_id == order_id).first()
        return order

    # 新增数据
    def insert(self):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)
        # 创建session对象:
        session = DBSession()
        # 添加到session:
        session.add(self)
        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()

    # 修改更新数据
    def update(self):
        json=self.tojson()
        print(json)
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        session.query(MyOrder).filter(MyOrder.order_id == self.order_id).update(json)
        session.commit()
        engine.dispose()

    # 保存
    def save(self):
        order=self.getdata(self.order_id)
        if order==None:
            self.insert()
        else:
            self.update()

    # 获取清仓股票
    def get_sellout_profit(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',start='2022-09-27',end='2022-09-29'):
        engine = create_engine(self.__connectString__)
        df_sellout = pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) as volume  FROM `myorder` WHERE STATUS=3 AND account_id='{}' AND trade_date>='{}' AND trade_date<='{}' GROUP BY symbol HAVING volume=0 order BY volume;".format(account_id,start,end), con=engine)

        df=pd.read_sql("SELECT * FROM `myorder` WHERE STATUS=3 AND account_id='{}' AND trade_date>='{}' AND trade_date<='{}'".format(account_id,start,end), con=engine)
        df_stock= df.loc[df['symbol'].isin(df_sellout['symbol'].values), :].copy()
        # engine.dispose()
        df_stock=df_stock.groupby(by=['symbol']).apply(lambda x:-(x['side']*x['volume']*x['price']).sum())
        # print(df_stock)

        df_profit = pd.DataFrame(data=df_stock)
        df_profit.reset_index(inplace=True)
        df_profit.columns=['symbol','profit']
        # print(df_gb.columns)
        # return df_profit['profit'].sum()
        return df_profit

    def get_day_sellout_stock(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',date=datetime.now().strftime('%Y-%m-%d')):
        engine = create_engine(self.__connectString__)
        df_sellout = pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) as volume  FROM `myorder` WHERE STATUS=3 AND account_id='{}' AND symbol IN (SELECT symbol FROM myorder WHERE STATUS=3 AND side=-1 AND account_id='{}' AND trade_date='{}') GROUP BY symbol HAVING volume=0 order BY volume;".format(account_id,account_id,date), con=engine)
        return df_sellout
        # print(df_sellout)

    def get_day_sellout_profit(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100',date=datetime.now().strftime('%Y-%m-%d')):
        df_sellout = self.get_day_sellout_stock(account_id=account_id, date=date)
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("SELECT * FROM `myorder` WHERE STATUS=3 AND account_id='{}' AND trade_date<='{}'".format(account_id, date), con=engine)
        symbols=stringutil.array_to_string(df_sellout['symbol'].values)
        symbols="'{}'".format(symbols.replace(',',"','"))
        df_sell=pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) as volume  FROM `myorder` WHERE STATUS=3 AND side=-1 AND account_id='{}' AND symbol IN ({}) AND trade_date='{}' GROUP BY symbol order BY volume;".format(account_id,symbols, date), con=engine)
        engine.dispose()

        df_out = df.loc[df.symbol.isin(df_sellout.symbol) & (df['side'] == 1), :].copy()
        df_ret = pd.DataFrame(columns=df_out.columns)

        df_ret=pd.concat([df_ret,df.loc[(df['trade_date']== date) & (df['side'] == -1) & (df['symbol'].isin(df_sell['symbol'])), :].copy()],axis=0,ignore_index=True)

        df_sell.set_index('symbol', inplace=True)

        for i,row in df_sellout.iterrows():
            df_symbol=df_out.loc[(df_out['symbol']==row['symbol']) ,:].copy()
            df_symbol.sort_values(by='updated_at', ascending=False,inplace=True)
            df_symbol['volume_cumsum']=df_symbol['volume'].cumsum()

            df_ret=pd.concat([df_ret,df_symbol.loc[df_symbol['volume_cumsum']<=-df_sell.at[row['symbol'],'volume'],:].copy()],axis=0,ignore_index=True)

        return df_ret

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
        df = pd.read_sql("SELECT account_id,COUNT(*) AS cnt FROM {} GROUP BY account_id ".format(self.__tablename__),
                         con=engine)
        engine.dispose()
        return df

if __name__ == '__main__':

    # StockPool().insert()
    # record=TradeRecord()
    # record.symbol='SHSE.600030'
    # record.side=1
    # record.price=11
    # record.volume=1000
    # record.amount=10000
    # record.trade_time=datetime.now()
    # record.record_time = datetime.now()
    # record.insert()
    # print(MyOrder().getAccountId())
    # df= MyOrder().get_day_sellout_stock(date='2022-09-29')
    df = MyOrder().get_day_sellout_profit(date='2022-09-29')
    # df=TradeRecord().getAccount()
    print(df)
    # loginfo(TradeRecord().getRecord())
    pass
