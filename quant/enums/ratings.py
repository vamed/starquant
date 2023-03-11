# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:股票评级枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique

@unique
class Ratings(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj

    BuyIn = '买入'
    SellOut = '卖出'
    Holding = '持有'
    Neutral = '观望'

if __name__=='__main__':
    print(Ratings.raising_limit.value)