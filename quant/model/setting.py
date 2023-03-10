# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:帐号交易参数设置类
# Copyright (C) 2021-2023
###############################################################################
#
import pandas as pd
from gm.enum import MODE_LIVE, MODE_BACKTEST
from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from quant.util.configutil import get_config

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class Setting(Base):
    # 指定本类映射到users表
    __tablename__ = 'setting'
    __connectString__=get_config('DATABASE','Tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    account_id = Column(String(50))
    max_position =Column(Float(5))
    max_single_position = Column(Float(5))
    max_stock_number=Column(Integer)
    per_buy_amount = Column(Float(10))
    memo = Column(String(200))
    name = Column(String(50))
    broker = Column(String(50))
    initial_capital=Column(Float(10))
    account_type=Column(Integer)


    def tojson(self):
        js = {'account_id': self.account_id, 'max_position': self.max_position,
              'max_single_position': self.max_single_position,'per_buy_amount': self.per_buy_amount,'memo': self.memo,'name': self.name,'broker': self.broker,'account_type': self.account_type}
        return js

    # 获取所有帐号设置
    def get_all_data(self):
        engine = create_engine(self.__connectString__)
        df=pd.read_sql("select * from setting",con=engine)
        engine.dispose()
        return df

    # 获取股票dataframe
    def getdata(self,account_id):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        setting = session.query(Setting).filter(Setting.account_id == account_id).first()
        return setting
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

    def update(self):
        json=self.tojson()
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        session.query(Setting).filter(Setting.account_id == self.account_id).update(json)
        session.commit()
        engine.dispose()

    def save(self):
        setting=self.getdata(self.account_id)
        if setting==None:
            self.insert()
        else:
            self.update()

    # 止损
    @classmethod
    def get_setting_accountid(self,context):
        ret = ""
        if context.mode==MODE_BACKTEST:
            ret="back_test"
        else:
            ret=context.account().id
        return ret

    # 获取当天发生的交易帐号
    def get_trade_account(self,date):
        engine = create_engine(self.__connectString__)
        # df=pd.read_sql("SELECT * FROM setting WHERE account_id IN (SELECT DISTINCT account_id FROM `order` WHERE trade_date='{}')".format(date),con=engine)
        df = pd.read_sql("SELECT * FROM setting ", con=engine)
        engine.dispose()
        return df
if __name__ == '__main__':
    s=Setting()
    # s=Setting().getdata("back_test")
    s.account_id="live"
    s.max_position = 0.5
    s.max_single_position = 0.5
    s.per_buy_amount = 0.5
    s.memo = "实时"
    print(s.tojson())
    df=pd.DataFrame( s.tojson(), )
    # df = json_normalize(s)

    print(df)
    # s.per_buy_amount=10000
    # # s.save()
    # setting = Setting().getdata("live")
    # print(setting.max_position)
    pass
    # Log().delete('2022-05-06',0)
    # d= Log().getdata('2022-05-06',0)
    # if d!=None:
    #     print(d.date)
