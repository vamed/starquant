# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:策略类型枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique

@unique
class Strategys(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj

    GridStrategy='GridStrategy'
    MeanRevertingStrategy = 'MeanRevertingStrategy'
    TrendFollowingStrategy = 'TrendFollowingStrategy'
    DayTradingStrategy= 'DayTradingStrategy'
