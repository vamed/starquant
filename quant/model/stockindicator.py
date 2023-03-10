# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:股票
# Copyright (C) 2021-2023
###############################################################################
#
import datetime

class StockIndicator():
    def __init__(self):
        self.symbol = ''
        self.open = ''
        self.close = ''
        self.low = ''
        self.high = ''
        self.volume = ''
        self.amount = ''
        self.eob = ''
        self.pre_close = ''
        self.k_pre = ''
        self.d_pre = ''
        self.j_pre = ''
        self.date = ''
        self.inflow = 0
        self.strategy=''
        self.stock_type=''
        self.minute_kdj=[]
        self.inflow_time = datetime.datetime.strptime("{} {}".format(datetime.datetime.now().strftime("%Y-%m-%d"),"09:30:00"),"%Y-%m-%d %H:%M:%S")

    # 'minute_kdj': self.minute_kdj,
    def to_json(self):
        js = {'symbol': self.symbol, 'open': self.open, 'close': self.close,
              'low': self.low, 'high': self.high,
              'volume': self.volume, 'amount': self.amount, 'eob': self.eob, 'pre_close': self.pre_close,
              'k_pre': self.k_pre,'d_pre': self.d_pre, 'j_pre': self.j_pre,  'date': self.date, 'inflow': self.inflow, 'strategy': self.strategy,'stock_type': self.stock_type, 'inflow_time': self.inflow_time}
        return js