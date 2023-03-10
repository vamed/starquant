# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:经纪商枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique

@unique  # @unique装饰器可以帮助我们检查保证没有重复值
class Brokers(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj
    # 掘金
    myquant = 'myquant'
    # 迅投qmt
    xtquant = 'xtquant'

if __name__=='__main__':
    # print(Factors.raising_limit.value)
    for b in Brokers:
        print(b.value)
