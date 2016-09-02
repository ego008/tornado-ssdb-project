# -*- coding: utf-8 -*-

from config import CONFIG

from common.base_handler import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):

        # if self.is_mobile:
        #     self.render('app_main/mobile/home.html', {
        #         'title': CONFIG.SITE_TITLE,
        #     }, layout='app_main/mobile/_layout.html')
        #     return

        self.render('app_main/web/home.html', {
            'title': CONFIG.SITE_TITLE,
        }, layout='app_main/web/_layout.html')
