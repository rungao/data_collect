#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导出项目的数据到MYSQL数据库中
"""

import sys
import configparser
import pymysql
import os
import os.path
import json
import logging


class ExportData:
    setting = {}
    date = sys.argv[1]
    db = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/mysql_config.ini', encoding='utf-8')
        for option in config.options('default'):
            self.setting[option] = config.get('default', option)

        self.db = pymysql.connect(self.setting['host'],
                                  self.setting['username'],
                                  self.setting['password'],
                                  self.setting['database']
                                  )

    def start(self):

        cursor = self.db.cursor()
        # 删除今日所有数据
        cursor.execute("DELETE FROM safe_rj_collect_data WHERE project_date = '%s'" % self.date)

        rootdir = "./data/" + self.date + '/'
        for parent, dirnames, filenames in os.walk(rootdir):
            for filename in filenames:
                file = os.path.join(parent, filename)
                for line in open(file, mode='r', encoding='utf-8'):
                    self._export(line)

        # 关闭mysql
        self.db.close()

    def _export(self, line):
        """导出所有数据到MYSQL"""
        data = json.loads(str(line).replace("'", "\""))
        project_date = self.date
        project_name = data['project_name']
        project_pos = data['project_pos']
        channel = data['channel']
        install_num = data['install_num']
        install_cpa = data['install_cpa']
        price_num = data['price_num']

        # 插入SQL
        insert_sql = "INSERT INTO safe_rj_collect_data(project_date, project_name, project_pos, channel, install_num, install_cpa, price_num) VALUES('%s', '%s', '%s','%s', '%s', '%s', '%s')" % (project_date, project_name, project_pos, channel, install_num, install_cpa, price_num)

        logging.info(insert_sql)

        cursor = self.db.cursor()

        try:
            cursor.execute(insert_sql)
            self.db.commit()
        except pymysql.InterfaceError as error:
            print("Error:" + error)
            self.db.rollback()

