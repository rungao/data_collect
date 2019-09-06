#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证码自动识别
https://www.jsdati.com/docs/sdk 联众识别
"""

import requests

import configparser
import json
import logging


class AutoCode:

    setting = {}

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/verity_setting.ini', encoding='utf-8')
        for option in config.options('default'):
            self.setting[option] = config.get('default', option)

    def get_code(self, file_name):
        """
            getCode() 参数介绍
            file_name       （需要识别的图片路径）   --必须提供
            api_post_url    （API接口地址）         --必须提供
            yzm_min         （识别结果最小长度值）        --可空提供
            yzm_max         （识别结果最大长度值）        --可空提供
            yzm_type        （识别类型）          --可空提供
            tools_token     （工具或软件token）     --可空提供
        """
        # https://account.jsdati.com/dashboard
        # 联众平台账号密码：
        api_username = self.setting['api_username']
        api_password = self.setting['api_password']
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }
        files = {
            'upload': (file_name, open(file_name, 'rb'), 'image/png')
        }
        api_post_url = self.setting['post_url']
        yzm_min = ''
        yzm_max = ''
        yzm_type = ''
        tools_token = ''
        data = {
            'user_name': api_username,
            'user_pw': api_password,
            'yzm_minlen': yzm_min,
            'yzm_maxlen': yzm_max,
            'yzmtype_mark': yzm_type,
            'zztool_token': tools_token
        }
        s = requests.session()
        r = s.post(api_post_url, headers=headers, data=data, files=files, verify=False)
        try:
            data = json.loads(r.text)
        except ValueError:
            logging.error('parse autocode error: ' + data)
        logging.info(data)
        if 'data' in data and 'val' in data['data']:
            code = data['data']['val']
        else:
            logging.error('fetch autocode error: ' + data)
            code = 0
        return code

