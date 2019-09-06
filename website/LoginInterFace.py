#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

import library.autocode
import requests
import os
from tempfile import NamedTemporaryFile
import json


class LoginInterFace(ABC):

    config = {}

    date = None

    header_base_data = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    post_data = {'userName': '', 'password': '', 'captcha': ''}

    cookie_data = {}

    @abstractmethod
    def start(self, config):
        pass

    @abstractmethod
    def get_header(self, config):
        pass

    @abstractmethod
    def login_admin(self):
        """登录后台方法"""
        pass

    @abstractmethod
    def get_captcha(self):
        pass

    @abstractmethod
    def get_admin_data(self):
        pass

    def get_captcha(self, code_url):
        """获取验证码方法"""
        return self._fetch_captcha(code_url)

    def get_url_stream(self, code_url):
        """获取验证码或者一个URL的流数据和COOKIE数据等"""
        res = requests.get(code_url)
        return res

    def save_data(self, channel, install_num, price_num, mode="w"):
        """保存获取到的数据到固定的目录进行保存"""
        """
        数据格式：
        {
          "project_name" : "合作项目名称",
          "project_pos" : "合作位置",
          "channel": "渠道号",
          "install_num": "安装量",
          "install_cpa": "单个应用安装的价格（XLS表格提供）",
          "price_num" : "汇总价格(部分厂家无则为空)"
        }
        """
        save_json_data = {
            "project_name": self.config['project_name'],
            "project_pos": self.config['project_pos'],
            "install_cpa": self.config['project_cpa'],
            "channel": channel,
            "install_num": install_num,
            "price_num": price_num
        }
        data_save_path = str(self.config['data_save_path']).replace('{date}', self.date)
        if not os.path.exists(os.path.dirname(data_save_path)):
            os.mkdir(os.path.dirname(data_save_path))

        file = open(data_save_path, mode=mode, encoding='utf-8')
        file.write(json.dumps(save_json_data) + "\n")
        file.close()

    def _fetch_captcha(self, context):
        """从第三方公司获取验证码-自动识别功能"""

        # 将文件流写入到临时文件夹中
        tmpfile = NamedTemporaryFile(delete=False)
        with open(tmpfile.name, "wb") as f:
            f.write(context)
        f.close()
        # 上传文件到验证码自助验证平台进行验证，并获取验证码识别文字
        auto_code = library.autocode.AutoCode()
        data = auto_code.get_code(tmpfile.name)
        tmpfile.close()
        return data

