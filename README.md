# starquant<星球量化>  

    starquant是基于掘金量化系统进行开发的量化交易框架，支持本地部署，支持断点回测，  
    支持自定义交易策略，选股数据及交易数据本地存贮及本地统计。   
[图文使用说明](https://articles.zsxq.com/id_dnsu1lupjbr9.html)   [视频使用说明](https://www.bilibili.com/video/BV1cb411o7oM/?vd_source=477f34fda05c82844e1e16ac83810323)

### 环境说明:

* 支持的系统版本：Windows 10

* 支持的Python版本： python 3.8 及以上版本

* 掘金客户端：v3.16	

* Mysql: v5.0.96

### 安装说明

* 必要库安装：
```
    pip install -r requirements.txt
```
### 使用说明
#### 掘金客户端配置：
1. 下载安装掘金客户端

    首先从[掘金官网](https://myquant.cn) 下载掘金客户端v3.16，安装并注册帐号，具体可参考[官网指引](https://myquant.cn/docs/guide/35#32961c39feb7af92)

2. 注册帐号并登录客户端创建一个模拟的交易帐号。

3. 新建一个空策略，并记录策略ID

4. 挂接策略到交易帐号
   
#### starquant量化交易框架参数设置：

1. 修改配置文件

    配置文件路径：\starquant\quant\config.ini

```
[TOKEN]
##掘金token
gmtoken = xxxxxx
[ACCOUNT]

##绑定帐号的交易策略id
strategy_id= 71878222-a222-222-2222-5811220c517b

##绑定帐号的交易策略id
backtest_strategy_id= 71878222-a222-222-2222-5811220c517b

##指定连接数据库信息
[DATABASE]
tradedb = mysql+mysqlconnector://root:111111@localhost:3306/starquant

##掘金客户端安装路径
[GOLDMINER]
path =D:\Goldminer3\Hongshu Goldminer3\goldminer3.exe
```

2. 数据库创建
    
  - 创建名称为starquantdb的空mysql数据库
        
  - 运行脚本数据库表：
```
    mysql -uroot -p111111 stockdb <  /iqunat/data/iquantdb.sql
```
3. 修改setting表中，帐号ID字段值为你掘金创建的模拟交易帐号ID

4. 交易标的股票代码设置：

    修改代码文件  starquant\quant\quantengine.py 可添加交易标的股票代码

5. 回测入口

    运行
```
python starquant\quant\startengine_bt.py
```

6. 实盘交易入口

运行
```
python starquant\quant\startengine_live.py
```
 
