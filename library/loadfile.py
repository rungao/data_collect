#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
每个项目加载的类配置信息
"""


class LoadFile:

    def wcdqq(self, config):
        """QQ浏览器-后台"""
        import website.wcdqq.login
        login = website.wcdqq.login.Login()
        login.start(config)

    def kuwo(self, config):
        """酷我音乐后台"""
        import website.kuwo.login
        login = website.kuwo.login.Login()
        login.start(config)

    def wps(self, config):
        """WPS后台"""
        import website.wps.login
        login = website.wps.login.Login()
        login.start(config)
