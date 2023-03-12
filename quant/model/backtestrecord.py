# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:回归记录
# Copyright (C) 2021-2023
###############################################################################
#

from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from quant.util.configutil import get_config

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class BacktestRecord(Base):
    # 指定本类映射到users表
    __tablename__ = 'backtest_record'
    __connectString__=get_config('DATABASE','tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    account_id = Column(String(50))
    start = Column(String(20))
    symbols = Column(String(200))
    current= Column(String(20))
    end =  Column(String(20))
    status = Column(String(20))
    date = Column(String(20))

    def insert(self):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)

        # 创建session对象:
        session = DBSession()
        session.add(self)
        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()

    def get_backtest_record(self,account_id):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine, expire_on_commit=False)
        session = DBSession()
        ret = session.query(BacktestRecord).filter(BacktestRecord.account_id == account_id).one()
        # session.commit()
        engine.dispose()
        return ret

    # 获取未完成的回测
    def get_suspend_record(self):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        ret = session.query(BacktestRecord).filter(BacktestRecord.status != 'finished').order_by(BacktestRecord.date.desc()).first()
        # session.commit()
        engine.dispose()
        return ret
    # 更新股票评级
    def update_backtest_record(self,account_id,date,status):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        js={"current": date,"status": status}
        session.query(BacktestRecord).filter(BacktestRecord.account_id == account_id).update(js)
        session.commit()
        engine.dispose()

if __name__ == '__main__':
    # b= BacktestRecord()
    # b.status="suspend"
    # b.account_id="dsssss"
    # b.date="2022-10-10"
    # b.start = "2021-10-10"
    # b.current = "2021-12-10"
    # b.end = "2022-10-10"
    # b.insert()
    b=BacktestRecord().get_suspend_record()
    # b=BacktestRecord().update_backtest_record(account_id='dsssss',date='2021-12-11',status='finished')
    if b==None:
        print(None)
    else:
        print(b.account_id)
    pass
