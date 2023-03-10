# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:交易方向枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique

#
@unique
class OrderSides(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj

    OrderSide_Unknown = 0
    OrderSide_Buy = 1  # 买入
    OrderSide_Sell = 2  # 卖出

if __name__=='__main__':
    pass
