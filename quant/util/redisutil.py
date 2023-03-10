import logging

from redis import StrictRedis

# 数据库连接方式 因为就算我自己使用的，所有没有设置密码
def getredis():
    redis = StrictRedis(host='localhost', port=6379, db=0, password='foobared')
    return redis

rd=getredis()
# rd.set('logging_level',logging.DEBUG)
rd.set('logging_level',logging.INFO)
dd=rd.get('logging_level')
# loginfo(dd)