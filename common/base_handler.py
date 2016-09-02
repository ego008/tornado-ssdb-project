# -*- coding: utf-8 -*-

from functools import wraps
import re
import time
import hmac
import uuid
import hashlib

import tenjin
from tenjin.helpers import escape, to_str, _decode_params
from tenjin.html import nl2br
from urllib import unquote

from tornado.web import Finish, HTTPError, RequestHandler, StaticFileHandler, decode_signed_value
from tornado.util import bytes_type, unicode_type
import json

from .property import CachedProperty
from .time_format import ts2date
from config import CONFIG
from core.ssdb_client import ssdb_main_client
from app_main.models.user import User


if CONFIG.DEBUG_MODE:
    Engine = tenjin.Engine
else:
    class Engine(tenjin.Engine):
        def _get_template_from_cache(self, cachepath, filepath):
            # skip file time checking
            return self.cache.get(cachepath, self.templateclass)

engine = Engine(path=[CONFIG.TEMPLATE_PATH], cache=tenjin.MemoryCacheStorage(), preprocess=True)

TEMPLATE_GLOBALS = {
    'to_str': to_str,
    'nl2br': nl2br,
    'escape': escape,
    '_decode_params': _decode_params,
    'CONFIG': CONFIG,
    'ts2date': ts2date,
}

MIME_TYPE_ABBREVIATIONS = {
    'atom': 'application/atom+xml',
    'html': 'text/html',
    'json': 'application/json',
    'plain': 'text/plain',
    'rss': 'application/rss+xml'
}


class BaseHandler(RequestHandler):

    _SPIDER_PATTERN = re.compile('(bot|crawl|spider|curl|apachebench|slurp|sohu-search|lycos|robozilla)', re.I)

    _secret = CONFIG.COOKIE_SECRET

    def _generate_id(self):
        new_id = hashlib.sha256(self._secret + str(uuid.uuid4()) + str(time.time()))
        return new_id.hexdigest()

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self._secret, hashlib.sha256).hexdigest()

    @CachedProperty
    def session(self):
        session_id = self.get_secure_cookie('session_id')
        hmac_key = self.get_secure_cookie('verification')

        if session_id and hmac_key:
            check_hmac = self._generate_hmac(session_id)
            if hmac_key != check_hmac:
                raise HTTPError(403)
        else:
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)

        self.set_secure_cookie('session_id', session_id)
        self.set_secure_cookie('verification', hmac_key)
        return session_id

    def head(self, *args, **kwargs):
        self.get(*args, **kwargs)

    def set_content_type(self, mime_type='text/html', charset='UTF-8'):
        mime_type = MIME_TYPE_ABBREVIATIONS.get(mime_type, mime_type)
        self.set_header('Content-Type', '%s; charset=%s' %
                        (mime_type, charset) if charset else mime_type)

    @CachedProperty
    def current_user_id(self):
        if CONFIG.COOKIE_SECRET:
            user_id = self.get_secure_cookie('user_id', min_version=2)
            if user_id:
                return user_id

            # user_id = self.get_secure_cookie("user_id")  # user_id
            # fixed no cookie value in User-Agent for Shockwave Flash and for lua upload
            if not user_id:
                secure_code = self.get_argument('code', '')  # code = self.get_cookie('user_id')
                if secure_code:
                    secure_user_id = unquote(secure_code)
                    user_id = decode_signed_value(self.application.settings["cookie_secret"], 'user_id', secure_user_id)
                    return user_id

    def get_current_user(self):
        user_id = self.current_user_id
        if user_id:
            return User.get_by_id(user_id)

    @CachedProperty
    def referer(self):
        return self.request.headers.get('Referer') or ''

    @CachedProperty
    def user_agent(self):
        return self.request.headers.get('User-Agent') or ''

    @CachedProperty
    def is_https(self):
        return self.request.protocol == 'https'

    @CachedProperty
    def is_xhr(self):
        requested_with = self.request.headers.get('X-Requested-With', '')
        return requested_with.lower() == 'xmlhttprequest'

    @CachedProperty
    def is_spider(self):
        if self.user_agent:
            return self._SPIDER_PATTERN.search(self.user_agent) is not None
        return False

    @CachedProperty
    def is_mobile(self):
        headers = self.request.headers
        if 'x-wap-profile' in headers or 'Profile' in headers or 'X-OperaMini-Features' in headers:
            return True

        user_agent = self.user_agent
        if user_agent:
            user_agent_lower = user_agent.lower()
            if 'phone' in user_agent_lower or 'mobi' in user_agent_lower or 'wap' in user_agent_lower:
                return True

            if 'is_mobile' in self.__dict__:
                return self.__dict__['is_mobile']

        return False

    @CachedProperty
    def in_weixin(self):
        if self.is_mobile:
            if 'micromessenger' in self.user_agent.lower():
                return True
        return False

    @property
    def db(self):
        return ssdb_main_client

    def write_json(self, value, ensure_ascii=False):
        self.finish(json.dumps(value, ensure_ascii=ensure_ascii))

    def render(self, template_name, context=None, globals=None, layout=False):
        if context is None:
            context = {'self': self}
        else:
            context['self'] = self
        if globals is None:
            globals = TEMPLATE_GLOBALS
        else:
            globals.update(TEMPLATE_GLOBALS)

        globals.update({
            'current_user_id': self.current_user_id,
        })
        self.finish(engine.render(template_name, context, globals, layout))

    def render2str(self, template_name, context=None, globals=None, layout=False):
        if context is None:
            context = {'self': self}
        else:
            context['self'] = self
        if globals is None:
            globals = TEMPLATE_GLOBALS
        else:
            globals.update(TEMPLATE_GLOBALS)
        return engine.render(template_name, context, globals, layout)

    def decode_argument(self, value, name=None):
        if value is None or isinstance(value, unicode_type):
            return value
        if not isinstance(value, bytes_type):
            raise TypeError(
                "Expected bytes, unicode, or None; got %r" % type(value)
            )
        return unicode(value, 'utf-8', 'replace')


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.send_error(404)


class BlankPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.set_status(204)

    post = get


def authorized(admin_only=False):
    def wrap(user_handler):
        @wraps(user_handler)
        def authorized_handler(self, *args, **kwargs):
            self.set_cache(is_public=False)
            request = self.request
            if request.method == 'GET':
                if not self.current_user_id:
                    next_url = self.get_argument('next', '/')
                    self.redirect(self.get_login_url() + "?next=" + next_url, status=302 if request.version == 'HTTP/1.0' else 303)
                elif admin_only and not self.is_admin:
                    raise HTTPError(403)
                else:
                    user_handler(self, *args, **kwargs)
            elif not self.current_user_id:
                raise HTTPError(403)
            elif admin_only and not self.is_admin:
                raise HTTPError(403)
            else:
                user_handler(self, *args, **kwargs)
        return authorized_handler
    return wrap
