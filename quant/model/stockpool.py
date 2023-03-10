# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:股票池类
# Copyright (C) 2021-2023
###############################################################################
#
import pandas as pd
from sqlalchemy import Column, Integer, String, create_engine, DateTime, Float, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from quant.util.configutil import get_config

Base = declarative_base()
# 定义映射类User，其继承上一步创建的Base
class StockPool(Base):
    # 指定本类映射到users表
    __tablename__ = 'stock_pool'
    __connectString__ = get_config('DATABASE', 'tradedb')

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    code = Column(String(20))
    symbol = Column(String(20))
    name = Column(String(20))
    change = Column(DECIMAL(6, 2))
    price = Column(Float(10))
    close = Column(Float(10))
    date = Column(String(20))
    strategy = Column(String(30))
    rating = Column(String(30))

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

    # 获取股票dataframe
    def getPositionStock(self):
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("SELECT * FROM pick_time WHERE strategy='by_holding'", con=engine)
        engine.dispose()
        return df

    # 获取股票dataframe
    def getStock(self):
        engine = create_engine(self.__connectString__)
        df = pd.read_sql('select * from pick_time', con=engine)
        engine.dispose()
        return df


    # 获取股票通过代码
    def get_stock_by_code(self, code):
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("select * from pick_time WHERE CODE='{}'".format(code), con=engine)
        engine.dispose()
        return df

    # 获取股票价格
    @classmethod
    def get_price(self, df, code):
        price = 0
        for i, row in df.iterrows():
            if row.code == code:
                price = row.price
        return price

    # 条件删除数据
    def delete(self, symbols=[]):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        session.query(StockPool).filter(StockPool.code.in_(symbols)).delete()
        session.commit()
        engine.dispose()

    # 条件删除数据
    def delete_all(self):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        # session.query(PickTime).filter(Teacher.id > 4).delete()
        session.query(StockPool).delete()
        session.commit()
        engine.dispose()

    def update(self, code, js):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        session.query(StockPool).filter(StockPool.code == code).update(js)
        session.commit()
        engine.dispose()

    # 批量插入股票池股票
    def batch_insert(self, df):
        engine = create_engine(self.__connectString__)
        df.to_sql(StockPool.__tablename__, engine, index=False, if_exists='append')
        engine.dispose()

    # 批量插入股票池股票
    def row_insert(self, row):
        engine = create_engine(self.__connectString__)
        row.to_sql(StockPool.__tablename__, engine, index=False, if_exists='append')
        engine.dispose()

    def get_picktime(self):
        engine = create_engine(self.__connectString__)
        df = pd.read_sql("select * from {} WHERE rating='{}'".format(self.__tablename__, "买入"), con=engine)
        engine.dispose()
        return df

    # 获取订单买入策略
    def get_symbols_strategy(self, symbols=[]):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        query = session.query(StockPool).filter(StockPool.symbol.in_(symbols))
        df = pd.read_sql(query.statement, engine)
        session.commit()
        engine.dispose()
        df.sort_values(by='date')
        df.drop_duplicates(subset=['symbol'], keep='last', inplace=True)
        df.set_index('symbol', inplace=True)
        df['stock_type'] = 'buyin'
        df['open_price'] = 0
        df = df.loc[:, ['strategy', 'rating', 'stock_type', 'open_price']]
        return df


if __name__ == '__main__':
        b = StockPool().get_symbols_strategy(['SZSE.000059'])
        print(b)
