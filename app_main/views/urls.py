# -*- coding: utf-8 -*-

from config import CONFIG

from common.base_handler import NotFoundHandler, StaticFileHandler

from .web.home import HomeHandler
from .web.user import LoginHandler, LogoutHandler, RegisterHandler
from .admin.home import AdminHomeHandler


STATIC_PATH = CONFIG.STATIC_PATH

handlers = [
    ('/', HomeHandler),

    (CONFIG.LOGIN_URL, LoginHandler),
    ('/register', RegisterHandler),
    ('/logout', LogoutHandler),

    ('/admin', AdminHomeHandler),

    (r'/(robots\.txt|favicon\.ico)', StaticFileHandler, {'path': STATIC_PATH}),
    (r'/static/(.*)', StaticFileHandler, {'path': STATIC_PATH}),

    (r'.*', NotFoundHandler)
]
