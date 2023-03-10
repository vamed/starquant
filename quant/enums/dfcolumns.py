from enum import Enum, unique

@unique
class DfColumns(Enum):
    def __new__(cls, value=None):
        obj = object.__new__(cls)
        # obj.english = value
        return obj

    close = 'close'
    dif = 'dif'
    dea = 'dea'
    macd = 'macd'
    k = 'k'
    d = 'd'
    j = 'j'
    # 分钟均价
    map = 'map'

if __name__=='__main__':
    print(DfColumns.macd.value)