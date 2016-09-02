# -*- coding: utf-8 -*-

from common.logger import log_request  # should be first statement to init logging

import os
import socket
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

try:
    sys.modules['json'] = __import__('ujson')
except ImportError:
    pass

import time
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

import tornado.httpclient
import tornado.ioloop
import tornado.netutil
import tornado.web

from common.http_server import HTTPServer
from config import CONFIG
from app_main.views.urls import handlers


__author__ = 'ego008@gmail.com'


def get_application():

    tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

    app = tornado.web.Application(
        handlers,
        debug=CONFIG.DEBUG_MODE,
        cookie_secret=CONFIG.COOKIE_SECRET,
        xsrf_cookies=CONFIG.XSRF_COOKIES,
        gzip=CONFIG.GZIP,
        template_path=CONFIG.TEMPLATE_PATH,
        static_path=CONFIG.STATIC_PATH,
        login_url=CONFIG.LOGIN_URL,
        log_function=log_request,
    )

    return app


def get_port():
    if len(sys.argv) >= 2:
        port = sys.argv[1]
        if port.isdigit():
            port = int(port)
            if port < 65535:
                return port
    return CONFIG.PORT


def main():
    application = get_application()
    port = get_port()

    if CONFIG.IPV4_ONLY:
        family = socket.AF_INET
    else:
        family = socket.AF_UNSPEC

    if CONFIG.DEBUG_MODE:
        address = None
    else:
        address = 'localhost'

    sockets = tornado.netutil.bind_sockets(port, address, family=family)
    server = HTTPServer(application, xheaders=CONFIG.XHEADERS)
    server.add_sockets(sockets)
    server.listen_exit_signal(CONFIG.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
