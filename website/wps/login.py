#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本流程：
1、模拟请求登录的验证码地址，无验证码验证的可请求登录页面，获取到验证码流和cookie信息
2、将验证码流提交验证码识别平台进行验证
3、模拟请求登录地址，带上自动识别的验证码、请求验证码的cookie信息（这点很重要）、header信息和账号信息
4、登录成功后同样每次请求后台地址必须带上cookie，获取对应数据


"""

from website.LoginInterFace import *
import requests
import logging
import sys
import re


class Login(LoginInterFace):

    def start(self, config):
        """入口"""
        self.date = sys.argv[1]
        self.config = config
        self.login_admin()
        self.get_admin_data()

    def get_header(self):
        """自定义的header配置"""
        header = {
            'Host': self.config['host'],
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Sec-Fetch-Mode': 'cors',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.config['admin_url'],
            'Origin': self.config['admin_url']
        }
        return header.update(self.header_base_data)

    def login_admin(self):
        """登录到后台的具体方法"""
        logging.info("login %s start..." % self.config['login_url'])
        s = requests.session()
        logging.info("get verify start " + self.config['verify_code_url'])

        # 获取cookie信息
        verify_res_data = self.get_url_stream(self.config['admin_url'])
        self.cookie_data = verify_res_data.cookies

        post_url = self.config['login_url']
        post_data = {
            'callCount': '1',
            'page': '/user.htm?method=index',
            'httpSessionId': requests.utils.dict_from_cookiejar(self.cookie_data)['JSESSIONID'],
            'scriptSessionId': '426B14C9F43C9FE6709259420A643DD1870',
            'c0-scriptName': 'UserAction',
            'c0-methodName': 'isUser',
            'c0-id': '0',
            'c0-param0': 'string:' + self.config['account_id'],
            'c0-param1': 'string:' + self.config['password'],
            'c0-param2': 'boolean:true',
            'batchId': '0'
        }

        # 登录需要带上请求验证码的cookie信息，不然就是一个新请求，会出现验证码验证失败
        # WPS使用的是payload方式提交数据的
        # 关于payload与Form Data的区别请见：https://blog.csdn.net/zwq912318834/article/details/79930423
        res = s.post(post_url,
                     data=post_data,
                     headers=self.get_header(),
                     cookies=requests.utils.dict_from_cookiejar(verify_res_data.cookies),
                     verify=False
                     )

        logging.info("login result:" + res.text)

    def get_admin_data(self):
        """获取具体数据的方法"""
        logging.info("get admin data start ...")
        s = requests.session()
        url = str(self.config['data_fetch_url']).replace('{date}', str(self.date).replace('-', ''))
        logging.info("date fetch url:" + url)

        # 一次登录通过多次选择不同的值获取到不到的值，并存入到同一个文本中

        channel_list = ['60.1897', '20.2665', '20.2666', '20.2667', '20.2668']

        for i in range(len(channel_list)):
            post_data = {
                'callCount': '1',
                'page': '/user.htm?method=yeji',
                'httpSessionId': requests.utils.dict_from_cookiejar(self.cookie_data)['JSESSIONID'],
                'scriptSessionId': '426B14C9F43C9FE6709259420A643DD1870',
                'c0-scriptName': 'UserAction',
                'c0-methodName': 'query',
                'c0-id': '0',
                'c0-param0': 'string:' + self.date,
                'c0-param1': 'string:' + self.date,
                # 推广方式
                'c0-param2': 'string:5',
                # 选择产品
                'c0-param3': 'string:1',
                # 通道号
                'c0-param4': 'string:' + channel_list[i],
                'c0-param5': 'string:9915',
                'c0-param6': 'string:1',
                'c0-param7': 'string:10',
                'batchId': '6'
            }

            res = s.post(url, data=post_data, headers=self.get_header(), cookies=self.cookie_data)

            logging.info('get admin data result:' + res.text)

            try:
                # WPS返回的格式是JS（代码写的真锉），通过正则方式匹配需要的值
                # install_num:有效安装 price_num:收入channel：渠道
                channel = re.search("s0\.channel\=\"(.*?)\"", res.text).group(1)
                price_num = re.search("s1\.fee\=\"(.*?)\"", res.text).group(1)
                install_num = re.search("s1\.result\=\"(.*?)\"", res.text).group(1)
                logging.info("channel:" + channel + "fee:" + price_num + "result:" + install_num)
                if channel and install_num and price_num:
                    # 保存数据，多个数据保存到一个文件中，追加模式
                    mode = "w" if i == 0 else "a"
                    self.save_data(channel=channel, install_num=install_num, price_num=price_num, mode=mode)
                else:
                    logging.error('admin data parse error')
            except Exception:
                pass


        logging.info("get admin data end")

