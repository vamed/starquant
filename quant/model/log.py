# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:日志类
# Copyright (C) 2021-2023
###############################################################################
#
import datetime
from sqlalchemy import Column, Integer, String, create_engine,DateTime,Float,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from quant.util.configutil import get_config

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class Log(Base):
    # 指定本类映射到users表
    __tablename__ = 'log'
    __connectString__=get_config('DATABASE','Tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    date = Column(String(50))
    record_time =Column(DateTime)
    result = Column(Integer)
    type = Column(Integer)
    memo = Column(String(500))

    # 获取股票dataframe
    def getdata(self,date,type):
        # 初始化数据库连接:
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        datacrawlLog = session.query(Log).filter(Log.date == date).filter(Log.type == type).filter(Log.result == 0).first()
        session.close()
        return datacrawlLog
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

    #删除数据
    def delete(self,date,type):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        session.query(Log).filter(Log.date==date).filter(Log.type==type).delete(synchronize_session=False)
        session.commit()
        engine.dispose()

    # log操作
    def log_operation(self,type,result,memo):
        dl = Log()
        dl.record_time = datetime.datetime.now()
        dl.type=type
        dl.result = result
        dl.date=datetime.datetime.now().strftime("%Y-%m-%d")
        dl.memo = memo
        dl.insert()

    # 每天数据更新结果检查
    def check_log(self,date,type):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)

        dl = Log()
        dl.record_time = datetime.datetime.now()
        dl.type=1
        # if len(result)==0:
        #     dl.result = 0
        #     dl.memo = '成功更新所有数据'
        # else:
        #     dl.result = 1
        #     str2 = ','
        #     memo = str2.join(result)
        #     dl.memo = memo
        dl.date=date
        Log().delete(date, 1)
        dl.insert()

if __name__ == '__main__':
    Log().delete('2022-05-06',0)
    d= Log().getdata('2022-05-06',0)
    if d!=None:
        print(d.date)
