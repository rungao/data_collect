#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全卫士后台自动登录并抓取数据
"""

import configparser
import urllib3
import logging
import sys,os,time
import library.loadfile
import library.autocode
import library.export

class ScrapySafeData:
    login_setting_project = []
    login_setting = {}

    def __init__(self):
        self.set_login_setting()
        urllib3.disable_warnings()

    def set_login_setting(self):
        """获取login_setting配置值"""
        config = configparser.ConfigParser()
        config.read('./config/login_setting.ini', encoding='utf-8')
        self.login_setting_project = config.sections()

        for section in self.login_setting_project:
            items = {}
            for option in config.options(section):
                items[option] = config.get(section, option)
            self.login_setting[section] = items

    def is_valid_date(self, str):
        """判断是否是一个有效的日期字符串"""
        try:
            time.strptime(str, "%Y-%m-%d")
            return True
        except:
            return False

    def start(self):
        for section in self.login_setting_project:
            loadf = library.loadfile.LoadFile()
            configf = self.login_setting[section]
            logging.info(section + "fetch data process start ...")
            if self.login_setting[section]['project_code'] == 'wcdqq':
                loadf.wcdqq(configf)
            elif self.login_setting[section]['project_code'] == 'kuwo':
                loadf.kuwo(configf)
            elif self.login_setting[section]['project_code'] == 'wps':
                loadf.wps(configf)
            logging.info(section + "fetch data process end")


if __name__ == '__main__':
    collect = ScrapySafeData()

    if len(sys.argv) != 2 or not collect.is_valid_date(sys.argv[1]):
        logging.error("date format is Y-m-d ...")
        sys.exit()

    # todo 第三个参数支持跑单个项目的数据，并导出

    logging.basicConfig(
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
        level=logging.INFO
    )

    logging.info("safe data fetch start ...")

    collect.start()

    # 导出数据
    export = library.export.ExportData()
    export.start()

    logging.info("safe data fetch end")
