import sys,os
import pandas as pd
base_dir=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))#获取pathtest的绝对路径
sys.path.append(base_dir)#将pathtest的绝对路径加入到sys.path中

from quant.logger import Logger
# 单步插入数据
def to_sql_by_step(df, tablename,engine):
    df.reset_index(drop=True,inplace=True)
    for i, r in df.iterrows():
        row = df.loc[i:i, :]
        try:
            row.to_sql(tablename, engine, index=False, if_exists='append')
        except Exception as e:
            # logerror('to_sql_by_step(self,df,tablename)：{}'.format(e))
            Logger().logerror(e)


# 保存数据到本地文件
def to_csv(df,filename):
    try:
        file="{}/data/{}".format(base_dir,filename)
        df.to_csv(file)
    except Exception as e:
        Logger().logerror('获取北向个股资金流：{}'.format(e))

# 生成数据文件名
def get_filename(table_name,date,squence=None):
    if squence==None:
        file="{}-{}.csv".format(table_name,date)
    else:
        file="{}-{}-{}.csv".format(table_name,squence,date)
    return file

# 添加对象实例到dataframe
def append_object_instance(df,obj):
    ls = dir(obj)
    vals = []
    keys = []
    for attr in ls:
        if attr[0:2] != '__':
            keys.append(attr)
            vals.append(getattr(obj, attr))
    srs = pd.Series(data=vals, index=keys)
    df=df.append(srs, ignore_index=True)
    return df

# 添加对象实例到dataframe
def append_from_dic(df,dict):
    df_dict=pd.DataFrame(dict,index=[0])
    df=pd.concat([df,df_dict],ignore_index=True)
    return df

# 添加对象实例到dataframe
def obj_to_series(obj):
    ls = dir(obj)
    vals = []
    keys = []
    for attr in ls:
        if (attr[0:2] != '__') and (attr !='data'):
            keys.append(attr)
            vals.append(getattr(obj, attr))
    series = pd.Series(data=vals, index=keys)
    return series
# 获取某列第一个值
def get_df_col_value(df,col_judge,value,column):
    ret=0
    for i,row in df.iterrows():
        if row[col_judge]==value:
            ret=row[column]
            break
    return ret

# dict转类对象
def dict_to_object(cls,dict):
    obj=cls()
    obj.__dict__=dict
    return obj

# 获取 df中某行记录并转实类实例
def get_obj_from_df(df,cls):
    # df=df.loc[df[col]==val,:]
    records=df.to_dict(orient ='records')
    obj=dict_to_object(cls,records[0])
    return obj

def list_to_df(v):
    if isinstance(v, list):
        return pd.DataFrame(data=v)
    elif isinstance(v, dict):
        return pd.DataFrame(data=[v, ])
    else:
        return pd.DataFrame(data=[{'value': v}])

# if __name__=="__main__":
#     to_csv("","")