from pytdx.hq import TdxHq_API
from quant.api.singleton import singleton
from quant.util import stockutil
from quant.util.pdutil import list_to_df
import pandas as pd
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 1000)

# 通达信接口
@singleton
class TdxApi():

    # 初始化通达信行情API接口
    def __init__(self):
        self.api = TdxHq_API()
        # self.api.connect('119.147.212.81', 7709)
        self.api.connect('123.125.108.91', 7709)

    # 查询分笔数据
    def get_transaction_data(self,symbol):
        count=1800
        market=stockutil.getMarketFromGmSymbol(symbol)
        code=stockutil.delSymbolPrefix(symbol)
        df = list_to_df(self.api.get_transaction_data(market, code,0,count))
        i=1
        while True:
            td=self.api.get_transaction_data(market, code,count*i,count*(1+1))
            if td==None:
                break
            else:
                df_temp=list_to_df(td)
                if (df.at[0,'time']==df_temp.at[0,'time']) & (df.at[0,'vol']==df_temp.at[0,'vol']):
                    break
                else:
                    df = pd.concat([df_temp, df], ignore_index=True)
                    i=i+1
                    if (len(df_temp))<count:
                        break
        if len(df)>0:
            df['amount']=df['price']*df['vol']
        return df

    # 获取公司文件返回目标节点内容
    def get_company_info_section(self,symbol,section_name):
        ret=None
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dicts=self.api.get_company_info_category(market_code,stock_code)
        for dict in dicts:
            if dict['name']==section_name:
                ret=dict
        #         name,filename,start,length
        return ret

    # 获取股本数
    def get_stock_quantity_change(self,symbol):
        section_name="股本结构"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        pos=ret.find('【2.股本变化】')
        ret=ret[pos:len(ret)]
        start_symbol='├──────┼─────────┼─────────┼─────────┼──────────────────────┤'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└──────┴─────────┴─────────┴─────────┴──────────────────────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.columns=['变更日期','总股本(股)','流通A股(股)','限售股份(股)','变更原因']
        # ret.split('\r\n')[1].split('｜')
        # print(df)
        return df

    # 获取股东变更
    def get_stock_holder_change(self,symbol):
        section_name="主力追踪"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        pos=ret.find('【2.股东户数变化】')
        ret=ret[pos:len(ret)]
        start_symbol='├───────┼────────┼────────┼────────┼──────┼────────┼────────┤'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────┴────────┴────────┴────────┴──────┴────────┴────────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.columns=['截止日期','股东户数(户)','变动户数(户)','变动幅度(%)','股价(元)','户均流通股(股) ','较上期变化（%) ']
        # ret.split('\r\n')[1].split('｜')
        # print(df)
        return df

    # 获取增发信息
    def get_spo(self,symbol):
        section_name="资本运作"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【1.募集资金来源】',beg)
        ret=ret[pos:len(ret)]
        if (ret.find('暂无数据')>-1) and ret.find('暂无数据')<20:
            # 没有数据
            return None
        start_symbol='├──────┼──────────────┼──────┼──────────────┼───────────────┤'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└──────┴──────────────┴──────┴──────────────┴───────────────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.columns=['公告日期','资金来源类别','发行起始日','发行价(元)','实际募集资金净额(元)']
        # ret.split('\r\n')[1].split('｜')
        # print(df)
        return df

    # 获取财务主标
    def get_financial_indicator(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【主要财务指标】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:-1, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        df.columns=['日期','审计意见','净利润','净利润增长率','扣非净利润','营业总收入','营业总收入增长率','加权净资产收益率','资产负债比率','净利润现金含量','基本每股收益','每股收益-扣除','稀释每股收益','每股资本公积金','每股未分配利润','每股净资产','每股经营现金流量','经营活动现金净流量增长率']
        return df

    # 获取偿债能力指标
    def get_solvency_indicator(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【偿债能力指标】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','流动比率','速动比率','资产负债比率(%)','产权比率(%)']
        return df

    # 获取运营能力指标
    def get_operational_capacity_indicator(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【运营能力指标】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','存货周转率','流动资产周转率','固定资产周转率','总资产周转率','每股现金流量增长率(%)']
        return df

    # 获取盈利能力指标
    def get_profitability_indicator(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【盈利能力指标】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','营业利润率','营业净利率','营业毛利率','成本费用利润率','总资产报酬率','加权净资产收益率']
        return df

    # 获取发展能力指标
    def get_development_capacity_indicator(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【发展能力指标】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','营业收入增长率','总资产增长率','营业利润增长率','净利润增长率','净资产增长率']
        return df

    # 获取资产负债表摘要
    def get_balance_heet_summary(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【资产负债表摘要】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','资产总额','货币资金','应收票据及应收账款','预付账款','其他应收款','存货','流动资产总额','固定资产','负债总额','应付票据及应付账款','预收帐款','合同负债','流动负债','非流动负债','未分配利润','盈余公积金','母公司股东权益','少数股东权益','股东权益合计','商誉','在建工程(净额)','可出售金融资产']
        return df

    # 获取利润表摘要
    def get_profit_heet_summary(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【利润表摘要】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','营业收入','营业成本','营业费用','管理费用','财务费用','投资收益','营业利润','营业外收支净额','利润总额','净利润']
        return df

    # 获取现金流量表摘要
    def get_cash_flow_statement(self,symbol):
        section_name="财务分析"
        market_code= stockutil.getMarketFromGmSymbol(symbol)
        stock_code=stockutil.delSymbolPrefix(symbol)
        dict=self.get_company_info_section(symbol,section_name)
        ret = self.api.get_company_info_content(market_code,stock_code, dict['filename'], dict['start'], dict['length'])
        beg=ret.find('】★')
        pos=ret.find('【现金流量表摘要】',beg)
        ret=ret[pos:len(ret)]
        start_symbol='┌───────────┬───────┬───────┬───────┬───────┬───────┬───────┐'
        start=ret.find(start_symbol)+len(start_symbol)
        end=ret.find('└───────────┴───────┴───────┴───────┴───────┴───────┴───────┘')
        ret=ret[start:end]

        content_list=ret.split('\r\n')
        for s in content_list:
            if s.find("｜")==-1:
                content_list.remove(s)
        df = pd.DataFrame([item.split("｜") for item in content_list])
        df=df.iloc[:, 1:-1]
        df.set_index(df[1], inplace=True, drop=True)
        df.drop(columns=[1], axis=1, inplace=True)
        df = df.T
        df.reset_index(drop=True, inplace=True)
        # print(df)
        df.columns=['日期','销售商品收到现金','经营活动现金流入','经营活动现金流出','经营活动现金净额','投资活动现金流入','投资活动现金流出','投资活动现金净额','筹资活动现金流入','筹资活动现金流出','筹资活动现金净额','汇率变动的现金流','现金流量净增加额']
        return df


if __name__=="__main__":
    #
    # code='SHSE.000001'
    # df = TdxApi().get_profit_heet_summary(code)
    # # df=TdxApi().get_cash_flow_statement(code)
    # print(df)

    # df.drop(columns=[0], axis=1, inplace=True)
    # # df.reset_index(inplace=True)
    # print(df)
    api = TdxHq_API()
    if api.connect('119.147.212.81', 7709):
        # df=api.get_company_info_category(TDXParams.MARKET_SH, '688008')
        df=api.get_security_quotes([(0, '000001')])
        # df=api.get_k_data('000001','2017-07-03','2017-07-10')
        # df=api.get_index_bars(9, 1, '886016', 1, 2)

        print(df)
        # data = TdxApi().api.get_security_bars(9, 0, '000001', 0, 10)  # 返回普通list
        # data1=list_to_df(TdxApi().api.get_transaction_data(TDXParams.MARKET_SH, '688008', 2000, 6000))
        # data1=api.to_df(api.get_history_transaction_data(TDXParams.MARKET_SH, '688008', 2000, 3000, 20220829))
        # df1=api.get_company_info_content(1, '688008', '688008.txt', 1016991, 27631)
        # print(df1)
    # df.to_csv("e:\\{}.csv".format(code))
    # print(df)