# -*- coding: utf-8 -*-

from datetime import timedelta
import os
import os.path


class ConfigMeta(type):
    def __init__(cls, name, bases, dct):
        super(ConfigMeta, cls).__init__(name, bases, dct)


class Config(object):
    __metaclass__ = ConfigMeta

    # application config
    DEBUG_MODE = True  # 开发时可设为 True，修改源码后会自动重启
    TEST = False  # 测试时设为 True，否则不能运行
    GZIP = True  # 生产环境应该设为 False，让 nginx 去 gzip，否则会丢失 ETag
    IPV4_ONLY = True  # 是否需要支持 IPv6
    XHEADERS = False  # 生产环境会在 nginx 传一些 X 开头的 header，此时建议开启
    PORT = 8081  # 默认运行的端口 8080
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 10  # 退出时如果还有没处理完的 callbacks，最长会等待多少秒
    COOKIE_SECRET = 'q288uy7gmlw21cxzyYuO7kaioPwmnaj23/AskzbT'  # cookie 的密钥，可以用 os.urandom(32) 生成
    XSRF_COOKIES = False  # POST 请求需要验证 xsrf

    # site config
    SITE_TITLE = u'网站标题'  # 网站标题
    SITE_SUB_TITLE = u'网站副标题'  # 网站副标题
    LANGUAGE = 'zh-cmn-Hans'  # 网站采用的主要语言

    LOGIN_URL = '/login'

    ADMIN_FLAG = 99  # 管理员flag
    ACTOR_FLAG = {99: '管理员', 50: '内部成员', 5: '正式会员', 0: '禁用会员'}  # 简单设置用户的标识

    # path config
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
    STATIC_PATH = os.path.join(PROJECT_PATH, 'static')

    # ssdb config
    SSDB_MAIN_DB = {'host': 'localhost', 'port': 8008}  # 存储数据的 SSDB 服务器地址

    # email config
    MAILGUN_API_BASE_URL = ''  # Mailgun API Base URL，可在 https://mailgun.com/ 申请
    MAILGUN_API_KEY = ''  # Mailgun API Key
    EMAIL_SENDER = ''  # 发件人邮件地址
    ADMIN_EMAIL = ''  # 管理员邮件地址

    # time config
    LOCAL_TIME_DELTA = timedelta(hours=8)  # 本地时区偏差
    DATE_FORMAT = '%Y-%m-%d'  # 日期格式
    SECOND_FORMAT = '%Y-%m-%d %H:%M:%S'  # 时间格式（精确到秒）
    MINUTE_FORMAT = '%Y-%m-%d %H:%M'  # 时间格式（精确到分）

    EACH_PAGE_SHOW_NUMBER = 10  # 每页显示的条数
