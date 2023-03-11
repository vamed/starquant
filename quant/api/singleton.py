# -*- encoding: utf-8 -*-
###############################################################################
# @author  : vamed
# @time    :2021-02-02
# @function:单例
# Copyright (C) 2021-2023
###############################################################################
#
def singleton(cls):
    _instance = {}  # 新建空字典; 不要_instance = None, 否则 inner 函数中赋值时，_instance 只会在函数作用域搜索，判断时会报错;

    def inner():  # 判断是否已有实例,如无,则新建一个实例并返回
        if cls not in _instance:
            _instance[cls] = cls()

        return _instance[cls]  # 返回的是实例对象

    return inner


if __name__=="__main__":
    @singleton
    class Cls():
        def __init__(self):
            pass  # 可以照常添加属性和方法


    cls1 = Cls()
    cls2 = Cls()
    print(cls1 is cls2 ) # True
