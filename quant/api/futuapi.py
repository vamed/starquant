from futu import *
import pandas as pd

from quant.api.singleton import singleton
from quant.logger import Logger

pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)

# 富途接口
@singleton
class FutuApi():
    # 拙金数据API封装
    # quote_ctx = None
    def __init__(self):
        self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    def get_stock_info(self,code_list):
        ret, data =self.quote_ctx.get_stock_basicinfo(market=Market.SH, code_list= code_list)
        if ret == RET_OK:
            data['code']=data['code'].apply(lambda x:x.split('.')[1])
            data.set_index('code',inplace=True)
            df=data.loc[:,['name']]
            # loginfo(df)
            return df
        else:
            Logger().loginfo('error:', data)
        # Logger().loginfo('******************************************')

    #获取资金流入量(单位是万)
    def get_stock_capital_in(self,code):
        ret, data = self.quote_ctx.get_capital_distribution(code)
        inflow=0
        if ret == RET_OK:
            inflow = round((data['capital_in_big'][0] + data['capital_in_mid'][0] + data['capital_in_small'][0] -
                            data['capital_out_big'][0] - data['capital_out_mid'][0] - data['capital_out_small'][
                                0]) / 10000, 2)
        return inflow

    #获取大单资金流入量(单位是万)
    def get_stock_capital_in_big(self,code):
        ret, data = self.quote_ctx.get_capital_distribution(code)
        inflow=0
        if ret == RET_OK:
            inflow = round((data['capital_in_big'][0] - data['capital_out_big'][0]) / 10000, 2)
        return inflow

    #获取大单资金流入量(单位是万)
    def get_rt_ticker(self,code):
        ret_sub, err_message = self.quote_ctx.subscribe(code, [SubType.TICKER], subscribe_push=False)
        # 先订阅逐笔类型。订阅成功后 FutuOpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
        if ret_sub == RET_OK:  # 订阅成功
            ret, data = self.quote_ctx.get_rt_ticker(code, 1000)  # 获取港股00700最近2个逐笔
            if ret == RET_OK:
                # print(data)
                # print(data['turnover'][0])  # 取第一条的成交金额
                # print(data['turnover'].values.tolist())  # 转为 list
                pass

            else:
                print('error:', data)
        else:
            print('subscription failed', err_message)

        return data
        # quote_ctx.close()  # 关闭当条连接，FutuOpenD 会在1分钟后自动取消相应股票相应类型的订阅

    def get_hostory_kline(self,symbol, start=None, end=None):
        ret=self.quote_ctx.request_history_kline(symbol, start=start, end=end, ktype=KLType.K_DAY, autype=AuType.QFQ, fields=[KL_FIELD.ALL],
                              max_count=1000, page_req_key=None, extended_time=False)
        df=ret[1]
        return df

    #
    def get_board(self,symbol_list):
        ret, data = self.quote_ctx.get_owner_plate(symbol_list)
        return data


if __name__=='__main__':
    # df=FutuApi().get_board(['SH.600030'])
    # print(df)
    # ret, data = self.quote_ctx.get_owner_plate(['SH.600030'])
    df=FutuApi().get_hostory_kline(symbol='SH.BK0047')
    print(df)



