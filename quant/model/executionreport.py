# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:交易事件回报
# Copyright (C) 2021-2023
###############################################################################
#
from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from quant.util.configutil import get_config

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class ExecutionReport(Base):
    # 指定本类映射到users表
    __tablename__ = 'execution_report'
    __connectString__=get_config('DATABASE','tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    account_id = Column(String(50))
    cl_ord_id = Column(String(50))
    symbol = Column(String(20))
    side = Column(Integer)
    mode = Column(Integer)
    price = Column(Float(10))
    volume = Column(Integer)
    amount = Column(Float(20))
    strategy=Column(String(50))
    trade_date = Column(String(50))
    trade_time = Column(DateTime,default=datetime.now())
    record_time= Column(DateTime,default=datetime.now())

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return "<ExecutionReport( account_id='%s',symbol='%s',name='%s',side='%s', price='%s',volume='%s', amount='%s',strategys='%s',trade_date='%s',trade_time='%s')>" % (
           self.account_id,self.symbol,self.name,self.side,self.price,self.volume,self.amount,self.strategy,self.trade_date,self.trade_time)

    def insert(self):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)

        # 创建session对象:
        session = DBSession()
        # 创建新User对象:
        # 添加到session:
        session.add(self)
        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()

    def getRecord(self,start=None,end=None,acount='d28f4b30-4bf9-11ec-ad1b-00163e0a4100'):
        engine = create_engine(self.__connectString__)
        where=''
        if start!=None:
            where="trade_date>='{}'".format(start)
        if end!=None:
            if where!='':
                where=where+' and '
            where=where+"trade_date<='{}'".format(end)
        if acount!="":
            if where != '':
                where = where + ' and '
            where = where + " account_id='{}'".format(acount)
        if where!='':
            where=" where {}".format(where)
        df=pd.read_sql("select * from {} {}".format(self.__tablename__,where),con=engine)
        engine.dispose()
        return df
    # 获取单个股票交易记录
    def getStockRecord(self,symbol,start=None,end=None):
        engine = create_engine(self.__connectString__)
        where=" symbol='{}'".format(symbol)
        if start!=None:
            where=where+" and trade_time>='{}'".format(start)
        if end!=None:
            where=where+" and trade_time<='{}'".format(end)
        if where!='':
            where=' where {}'.format(where)
        df=pd.read_sql("select * from {} {}".format(self.__tablename__,where),con=engine)
        engine.dispose()
        return df
    # 获取单个股票交易记录
    def hasExistTradeRecord(self,symbol,trade_time,amount):
        ret=False
        engine = create_engine(self.__connectString__)
        where="where symbol='{}' and trade_time='{}' and amount={} ".format(symbol,trade_time,amount)
        df=pd.read_sql("select * from trade_record {}".format(where),con=engine)
        engine.dispose()
        if len(df)>0:
            ret=True
        return ret
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
        df = pd.read_sql("SELECT account_id,COUNT(*) AS cnt FROM trade_record GROUP BY account_id ",
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
    # 获取单个股票交易记录
    def getTradeRecord(self,symbol,acount,start=None,end=None):
        engine = create_engine(self.__connectString__)
        where=" symbol='{}' and account_id='{}'".format(symbol,acount)
        if start!=None:
            where=where+" and trade_time>='{}'".format(start)
        if end!=None:
            where=where+" and trade_time<='{}'".format(end)
        if where!='':
            where=' where {}'.format(where)
        df=pd.read_sql("select * from trade_record {}".format(where),con=engine)
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

    # def batch_insert(self,df):
    #     for i,execrpt in df.iterrows():
    #         if execrpt.exec_type == 15:
    #             trade_record = ExecutionReport()
    #             trade_record.account_id = execrpt.account_id
    #             trade_record.cl_ord_id = execrpt.cl_ord_id
    #             trade_record.symbol = execrpt.symbol
    #             if execrpt.side == 1:
    #                 trade_record.side = 1
    #             elif execrpt.side == 2:
    #                 trade_record.side = -1
    #             trade_record.price = execrpt.price
    #             trade_record.volume = execrpt.volume
    #             trade_record.amount =Decimal(execrpt.amount).quantize(Decimal('0.00'))
    #             trade_record.trade_date = execrpt.created_at.strftime('%Y-%m-%d')
    #             trade_record.record_time =datetime.now()
    #             trade_record.trade_time=pd.to_datetime(execrpt.created_at).strftime('%Y-%m-%d %H:%M:%S')
    #             if ExecutionReport().hasExistTradeRecord(trade_record.symbol, trade_record.trade_time,
    #                                                  trade_record.amount) == False:
    #                 try:
    #                     trade_record.insert()
    #                 except Exception as e:
    #                     logerror('交易记录保存错误：{}'.format(e))
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
    print(ExecutionReport().getAccountId())
    df= ExecutionReport().hasExistTradeRecord('SHSE.600743','2022-05-17 13:52:07.693056',33120)
    # df=TradeRecord().getAccount()
    print(df)
    # loginfo(TradeRecord().getRecord())
    pass
