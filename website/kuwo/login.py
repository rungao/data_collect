#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本流程：
1、模拟请求登录的验证码地址，无验证码验证的可请求登录页面，获取到验证码流和cookie信息
2、将验证码流提交验证码识别平台进行验证
3、模拟请求登录地址，带上自动识别的验证码、请求验证码的cookie信息（这点很重要）、header信息和账号信息
4、登录成功后同样每次请求后台地址必须带上cookie，获取对应数据

Beautiful Soup 是能解析HTML到Python格式的库，具体请看：https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html

"""

from website.LoginInterFace import *
import requests
import logging
import json
import sys
from bs4 import BeautifulSoup


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

        # 获取cookies和验证码流
        verify_res_data = self.get_url_stream(self.config['admin_url'])
        self.cookie_data = verify_res_data.cookies

        post_url = self.config['login_url']
        post_data = {
            'username': self.config['account_id'],
            'password': self.config['password'],
            'forward': '',
            'type': 'Puser'
        }

        # 登录需要带上请求验证码的cookie信息，不然就是一个新请求，会出现验证码验证失败
        res = s.post(post_url,
                     data=post_data,
                     headers=self.get_header(),
                     cookies=requests.utils.dict_from_cookiejar(self.cookie_data),
                     verify=False
                     )

        logging.info("login result:" + res.text)

    def get_admin_data(self):
        """获取具体数据的方法"""
        logging.info("get admin data start ...")
        s = requests.session()
        url = str(self.config['data_fetch_url']).replace('{date}', str(self.date).replace('-', ''))
        logging.info("date fetch url:" + url)

        channel_list = ['2345duote-12', '2345duote-07', '2345duote-08', '2345duote-09']

        for i in range(len(channel_list)):
            # query_ptime=2019-08-14+%E8%87%B3+2019-08-14&query_pname=2345duote-12
            post_data = {
                'query_ptime': self.date + ' 至 ' + self.date,
                'query_pname': channel_list[i]
            }
            # 带上登录的COOKIE信息
            res = s.post(url, data=post_data, headers=self.get_header(), cookies=self.cookie_data)
            logging.info('get admin data result:' + res.text)
            # 酷我返回的是HTML代码（更矬），需要通过BeautifulSoup解析DIV代码
            soup = BeautifulSoup(res.text, "html.parser")
            # install_num:有效安装 price_num:收入channel：渠道

            try:
                price_num = str(soup.select('tr td')[4].string).replace(' ', '').replace('元', '')
                install_num = soup.select('tr td')[2].string
                channel = soup.select('tr td')[0].string
                if channel and price_num and install_num:
                    # 保存数据，多个数据保存到一个文件中，追加模式
                    mode = "w" if i == 0 else "a"
                    self.save_data(channel=channel, install_num=install_num, price_num=price_num, mode=mode)
                else:
                    logging.error('admin data parse error')
            except Exception:
                pass

        logging.info("get admin data end")

