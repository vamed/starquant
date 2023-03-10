# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:持仓类
# Copyright (C) 2021-2023
###############################################################################
#

from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine, DateTime, Float, DECIMAL, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datacompy
from quant.util.configutil import get_config
Base = declarative_base()

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)
# 定义映射类User，其继承上一步创建的Base
class Position(Base):
    # 指定本类映射到users表
    __tablename__ = 'position'
    __connectString__=get_config('DATABASE','tradedb')
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id= Column(String(50))
    # 指定name映射到name字段; name字段为字符串类形，
    code = Column(String(20))
    symbol= Column(String(20))
    name = Column(String(20))
    #平均建仓成本
    open_price=Column(Float(10))
    # 持仓总数量
    volume=Column(Integer)
    amount=Column(Float(10))
    #可用数量
    can_use_volume=Column(Integer)
    # 冻结量
    frozen_volume = Column(Integer)
    # 昨量
    yesterday_volume= Column(Integer)
    # 当天量
    on_road_volume= Column(Integer)
    # 现价
    price = Column(Float(10))
    # 持仓市值(现值)
    market_value= Column(Float(10))

    # 持仓盈利
    profit_amount = Column(Float(20))
    profit_rate = Column(Float(10))

    # ------------------------------------
    inflow = Column(Float(20))
    factor = Column(String(30))
    rating = Column(String(30))
    strategy = Column(String(20))

    # pe = Column(Float(20))
    # holderchange = Column(Float(20))
    # # 公司利润
    # profit = Column(Float(20))
    # industry = Column(String(30))
    # industry_name = Column(String(30))
    date = Column(String(20))
    # seldate = Column(DateTime, default=datetime.now())
    update_time= Column(DateTime, default=datetime.now())
    created_at= Column(DateTime, default=datetime.now())
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

    # 批量插入股票池股票
    def batch_insert(self,df):
        engine = create_engine(self.__connectString__)
        df.to_sql(Position.__tablename__, engine, index=False, if_exists='append')
        engine.dispose()

    # 获取股票池股票
    def get_all_stock(self):
        engine = create_engine(self.__connectString__)
        df=pd.read_sql('select * from {}'.format(self.__tablename__),con=engine)
        engine.dispose()
        return df

    # 获取股票池股票
    def get_stock_by_code(self,code):
        engine = create_engine(self.__connectString__)
        df=pd.read_sql("SELECT * FROM {} WHERE CODE='{}' ".format(self.__tablename__,code),con=engine)
        engine.dispose()
        return df

    # 获取股票池股票
    def get_stock(self,start=None,end=None,factor=None):
        engine = create_engine(self.__connectString__)
        where=''
        if factor!=None:
            where = " factor='{}'".format(factor)
        if start != None:
            if where !='':
                where=where+" and "
            where = where + " seldate>='{}'".format(start)
        if end != None:
            if where != '':
                where = where + " and "
            where = where + " seldate<='{}'".format(end)
        if where != '':
            where = ' where {}'.format(where)
        df = pd.read_sql("select * from {} {}".format(self.__tablename__,where), con=engine)
        engine.dispose()
        return df

    # 删除代码列数据
    def delete(self,symbols=[]):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        session.query(Position).filter(Position.code.in_(symbols)).delete(synchronize_session=False)
        session.commit()
        engine.dispose()

    # 删除所有数据
    def delete_all(self,account_id):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        # session.query(Position).filter(text('1=1')).delete(synchronize_session=False)
        session.query(Position).filter(Position.account_id==account_id).delete(synchronize_session=False)
        session.commit()
        engine.dispose()

    #   查询并删除某策略的数据
    def delete_strategy(self,strategy):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        session.query(Position).filter(Position.strategy==strategy).delete(synchronize_session=False)
        session.commit()
        engine.dispose()

    # 更新股票评级
    def update(self,code,js):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        session.query(Position).filter(Position.code == code).update(js)
        session.commit()
        engine.dispose()

    def get_position(self):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        ret = session.query(Position).all()
        session.commit()
        engine.dispose()
        return ret

    #对象转json
    # @classmethod
    def to_json(self):
        js = {'account_id': self.account_id, 'code': self.code ,'symbol': self.symbol ,'profit_amount': self.profit_amount,'profit_rate': self.profit_rate ,
              'name': self.name ,'price': self.price ,'open_price': self.open_price,'volume': self.volume,'amount': self.amount,'can_use_volume': self.can_use_volume
              ,'frozen_volume': self.frozen_volume ,'on_road_volume': self.on_road_volume,'market_value': self.market_value,'update_time': self.update_time,'created_at': self.created_at }
        return js

    # 对象数组转dataframe
    @classmethod
    def to_df(self,pos):
        df=pd.DataFrame()
        if len(pos)>0:
            df=pd.DataFrame(pos[0].to_json(),index=[0])
            for i in range(len(pos)):
                if i>0:
                    # df=df.append(pd.DataFrame(pos[i].to_json(),index=[i]))
                    df=pd.concat([df,pd.DataFrame(pos[i].to_json(),index=[i])],axis=0,ignore_index=True)
            # df['symbol']=df['code'].apply(lambda x:stockutil.xtToGmSymbol(x))
        return df

    # 获取持仓策略及评级
    def get_symbols_strategy(self,account_id,symbols=[]):
        engine = create_engine(self.__connectString__)
        DBSession = sessionmaker(bind=engine)
        # 创建session对象
        session = DBSession()
        query = session.query(Position).filter(Position.account_id==account_id).filter(Position.symbol.in_(symbols))
        df = pd.read_sql(query.statement, engine)
        session.commit()
        engine.dispose()
        df.set_index('symbol',inplace=True)
        df['stock_type']='holding'
        df=df.loc[:,['strategy','rating','stock_type','open_price']]
        return df

    # 获取本地数据持仓数据
    def get_local_position(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100'):
        engine = create_engine(self.__connectString__)
        df_pos = pd.read_sql("SELECT * FROM `position` WHERE account_id='{}'".format(account_id), con=engine)
        engine.dispose()
        return df_pos

    # 检查持仓是否和交易记录一致
    def check_position_data(self,account_id='59ae65ad-c062-11ec-bde8-00163e0a4100'):
        engine = create_engine(self.__connectString__)
        df_ord = pd.read_sql("SELECT symbol,cast(SUM(side*volume) AS signed) AS volume  FROM `myorder` WHERE STATUS=3 AND account_id='{}' GROUP BY symbol HAVING volume>0 order BY volume".format(account_id), con=engine)
        df_pos = pd.read_sql("SELECT * FROM `position` WHERE account_id='{}'".format(account_id), con=engine)
        engine.dispose()

        # df_ord = df_ord.loc[:, ['symbol', 'volume']]
        print(df_ord)

        df_pos=df_pos.loc[:,['symbol','volume']]
        df_pos.sort_values(by='volume',ascending=True,inplace=True)
        print(df_pos)
        compare = datacompy.Compare(df_ord, df_pos, join_columns='volume')

        return compare.matches()
        # print(compare.matches())  # 最后判断是否相等，返回 bool
        # print(compare.report())  # 打印报告详情，返回 string

    # 获取缓存持仓信息
    def get_cache_position(self, positions, symbol):
        ret = None
        for pos in positions:
            if pos.symbol == symbol:
                ret = pos
                break
        return ret



if __name__ == '__main__':
    b= Position().get_symbols_strategy('62bbe5fb-3f95-11ed-976c-00163e18a8b3',['SZSE.002265','SZSE.002850','SHSE.601633'])
    print(b)
    # Position().delete(['002781', '002437', '002679', '300782', '000987', '600661', '000333', '600690', '601231', '600410', '603808', '399001', '000001'])
    # loginfo(StockPool().delete())
    pass
