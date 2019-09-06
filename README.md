# 说明
使用Python 3进行网站自动登录、自动识别验证码，并进行数据抓取，抓取后将数据保存到文本中，并统一导出到Mysql中存储。

# 需求点
产品提供一份XLS表格，一共约有50多个网站的登陆地址、账号、密码信息，该网站是软件管家与外部合作的每日数据信息，产品每日进行手动登录，耗费了较多时间，想使用自动化进行登录、进行数据爬取并获取数据到统一的后台进行查看。

## 方案设计
数据爬取联系了xx原开发伙伴，使用的是PHP进行爬取，拿到对应的代码进行查看后发现代码写的比较乱，复用性不强。

### 技术思考
数据爬取使用Python作为技术选型是最适合了，结合团队内对Python的熟悉，且Python的学习成本并不高，所以最终选型使用Python进行数据爬取。

### 架构设计

我们主要要解决的问题点：

1、 部分网站有验证码，该如何破解

2、 这么多网站爬取、不稳定因素较大，如何保证数据的正确性

3、如何支持网站的重复爬取、数据自动感知

4、要可配置性，接入一个新网站后应该只需要研究HTTP请求和修改相关配置即可


### 风险考虑
1、网站改版后无法获取到对应的信息

2、网站访问异常或者脚本出现访问异常无法获取数据

3、获取的数据出现了解析错误或者有重复的数据信息


## 实际编码

### 结构设计
1、 所有的网站可进行配置，新增网站只需要做两步：新增网站配置和复制抓数据的类进行修改即可

2、共用的方法要进行封装、可复用，减少耦合，比如数据保存、验证码获取、文件加载等

3、所有的过程有详细的日志记录，并对日志进行分类ERROR/INFO/WARN等，后续可进行日志的追踪

### 目录设计
```
2345_safe_data_collect
    |---- config 配置文件
        |---- login_setting.ini 50个网站的配置信息
        |---- verity_setting.ini 验证码配置信息
    |---- data 获取到的数据
        |---- Y-m-d 每日一个目录
    |---- library
        |---- autocode.py 验证码封装类
        |---- loadfile.py 自动加载类
        |---- export.py 数据统一导出
    |---- website
        |---- loginInterFace.py 抓数据抽象
        |---- wap/login.py
        抓数据实际代码（继承）
        ... 每个项目一个目录和login.py
    - README.md 说明文档
    - requirements.txt 依赖包
    - start.py Y-m-d 入口文件

```

### 配置文件

#### 网站的配置文件
```ini
[unicorn.wcd.qq.com]
project_name : QQ浏览器
project_pos: 管家
project_code: wcdqq
project_cpa: ******
account_id: ******
password: ******
host : unicorn.wcd.qq.com
admin_url : https://unicorn.wcd.qq.com/login.html
login_url : https://unicorn.wcd.qq.com/cloginverify.html
verify_code_url: https://unicorn.wcd.qq.com/captcha?date=1565746448696
data_fetch_url: https://unicorn.wcd.qq.com/free/getPayDataTable.html?timeArea={date}+-+{date}&product=&platform=&vendor=&channel=&datatype=d&dataValue=newUser&fee=&fileType=&pageSize=20&curPage=1
data_save_path: data/{date}/unicorn.wcd.qq.com-92762.txt
```

#### 验证码配置文件

```ini
[default]
dashboard: https://account.jsdati.com/dashboard
api_username: guanjia0812
api_password: yunying123_
post_url: http://v1-http-api.jsdama.com/api.php?mod=php&act=upload
```

### 网站分析

如果你熟悉HTTP协议，你就会知道浏览器登录网站的流程为：

第一步：用户打开登录页面

第二步：服务端返回set-cookie的header，浏览器将cookie设置保存到本地

第三步：用户输入账号密码登录，请求服务端

第四步：服务端返回认证成功，将用户的信息和SESSIONID进行关联保存到服务端中

第五步：用户可访问登录后的网页

**关键点：**先访问一个网页，拿到COOKIE后，后续登录包含拿数据都需要带上这个COOKIE即可。

某些网站除了使用COOKIE外还使用了特别的Header，特殊情况需要特殊分析。


### 验证码突破

验证码使用了第三方的验证码识别，原理是你把验证码通过接口上传到第三方平台，第三方平台识别后返回给你对应的验证码，价格为每条1分，还是比较优惠的，官网：https://account.jsdati.com

### 数据导出

1、数据生成的格式都进行统一格式，使用python mysql导出到mysql即可，非常简单

关键点：找出规律，所有的网站都定义相同的数据保存格式，这样数据导出就不用做兼容处理了。

参考格式：
```
{
  "project_name" : "合作项目名称",
  "project_pos" : "合作位置",
  "channel": "渠道号",
  "install_num": "安装量",
  "install_cpa": "单个应用安装的价格（XLS表格提供）",
  "price_num" : "汇总价格(部分厂家无则为空)"
}
```

## python部署

### 线上部署

第一步：本地生成需要依赖的包

pip freeze > requirements.txt


第二步：线上安装需要依赖的包

pip install -r requirements.txt

第三步：部署crontab运行python
> python3 start.py Y-m-d


## 知识点总结

## PayLoad与FormData区别
- Form Data: POST请求，每个参数以a=1&b=2格式链接，header头中有`Content-Type: application/x-www-form-urlencoded`格式
- Request Payload:POST请求，参数格式为JSON格式，如：`{"key":"value","key":"value"...}`, header头设置`Content-Type:application/json`

### Python相关类库使用

类库 | 说明
---|---
configparser | 解析INI格式文件库
logging | 日志记录库，类似php的mongolog
requests | POST/GET请求库
json | json格式解析库
sys,os,time | 系统相关类库
NamedTemporaryFile | 临时文件存储库
ABC | 实现抽象功能库
bs4 | Beautiful Soup 是能解析HTML到Python格式的库
re | 正则表达式库

### 源码地址
github待补充

# 相关工具
- 开发工具 PyCharm
- 抓包工具 Fiddler Wireshark
- Python版本 3.7
- Mysql 5.7

### 滑动验证码思考
Q：目前最新的网站如淘宝等各大网站已经不使用验证码登录功能了，使用的是点击验证或者滑动图片的方式进行验证，那么这种验证码该如何进行破解呢？

方法一：

与联众沟通，支持将图片提交给验证码平台，验证码平台返回对应的坐标，再由客户端拼接坐标提交到服务端进行验证

方法二：

可借鉴`Selenium`来模拟浏览器进行操作，手动点击后再自动操作进行验证

# 参考文献

- Python Scrapy爬虫框架 https://www.runoob.com/w3cnote/scrapy-detail.html
- Python + Requests 模拟登陆（含验证码） https://blog.csdn.net/qq_15718805/article/details/79004379
- Python模拟登录 https://blog.csdn.net/figo829/article/details/18728381