# -*- coding: utf-8 -*-

from config import CONFIG

from common.base_handler import BaseHandler

class AdminHomeHandler(BaseHandler):
    def get(self):
        self.render('app_main/admin/home.html', {
            'title': CONFIG.SITE_TITLE,
            'test': 'admin home content',
        }, layout='app_main/admin/_layout.html')

