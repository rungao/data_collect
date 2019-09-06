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
import json
import sys


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
        verify_res_data = self.get_url_stream(self.config['verify_code_url'])
        self.cookie_data = verify_res_data.cookies

        # 获取人工识别验证码
        verify_code = self.get_captcha(verify_res_data.content)
        logging.info("get verify result" + verify_code + " cookies:" + str(self.cookie_data))

        post_url = self.config['login_url']
        post_data = {
            'userName': self.config['account_id'],
            'password': self.config['password'],
            'captcha': verify_code
        }

        # 登录需要带上请求验证码的cookie信息，不然就是一个新请求，会出现验证码验证失败
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
        # 带上登录的COOKIE信息
        res = s.get(url, headers=self.get_header(), cookies=self.cookie_data)
        logging.info('get admin data result:' + res.text)

        try:
            data = json.loads(res.text)
            if 'data' in data:
                channel = data['data'][0]['channel']
                install_num = data['data'][0]['actCnt']
                price_num = 0
                self.save_data(channel=channel, install_num=install_num, price_num=price_num, mode="w")
        except Exception:
            logging.error('admin data parse error')
            pass

        logging.info("get admin data end")

