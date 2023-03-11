# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:策略作用范围枚举类
# Copyright (C) 2021-2023
###############################################################################
#
from enum import Enum, unique
#
@unique
class Scopes(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        return obj

    stock = 'stock'
    universal= 'universal'
