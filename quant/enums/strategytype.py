# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:策略驱动类型枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique
@unique  # @unique装饰器可以帮助我们检查保证没有重复值
class StrategyType(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj

    bar = 'bar'
    tick = 'tick'
    schedule = 'schedule'
