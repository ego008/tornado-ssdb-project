# -*- coding: utf-8 -*-

import json
import bcrypt
from time import time

from common.helper import match_user_name
from ...models.user import User

from common.base_handler import BaseHandler


class RegisterHandler(BaseHandler):
    def get(self):
        self.render('app_main/web/register.html', {
            'title': "注册",
        }, layout='app_main/web/_layout.html')

    def post(self):
        nt = int(time())
        name = self.get_argument('name', '')
        if not match_user_name(name):
            self.write({'code': 201, 'msg': '用户名格式不正确', 'url': ''})
            return

        act = self.get_argument('act', '')

        if act == 'register':
            #
            _error = []

            password = self.get_argument('password', '')
            password2 = self.get_argument('password2', '')
            if password and password2 and password == password2:
                pass
            else:
                _error.append('两次输入密码不一样')

            if _error:
                self.write({'code': 201, 'msg': ', '.join(_error), 'url': ''})
                return

            # 注册新用户
            max_id = int(self.db.hsize('user_info'))
            new_id = max_id + 1
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            x_real_ip = self.request.headers.get("X-Real-IP")
            remote_ip = x_real_ip or self.request.remote_ip

            if new_id == 1:
                flag = 99
            else:
                flag = 5  # 默认

            user = {
                'id': new_id,
                'name': name,
                'flag': flag,
                'password': hashed,
                'reg_time': nt,
                'reg_ip': remote_ip,
                'add_by': new_id,
            }

            self.db.hset('user_info', new_id, json.dumps(user))
            self.db.hset('user_name2id', name, new_id)
            self.db.zset('user_reg_time', new_id, nt)

            self.set_secure_cookie("user_id", str(user['id']))
            next_url = self.get_argument('next', '/')
            self.write({'code': 200, 'url': next_url})

            return

        self.write({'code': 400, 'msg': '', 'url': ''})


class LoginHandler(BaseHandler):
    def get(self):
        self.render('app_main/web/login.html', {
            'title': "登录",
        }, layout='app_main/web/_layout.html')

    def post(self):
        rsp = {'code': 401, 'msg': '', 'url': ''}
        name = self.get_argument('name')
        password = self.get_argument('password')
        if name and password:
            if match_user_name(name):
                name_lower = name.lower()
                user = User.get_by_name(name_lower)
                if user:
                    password = password.encode()
                    if bcrypt.hashpw(password, user['password'].encode()) == user['password']:
                        # It Matches!
                        # set cookie
                        self.set_secure_cookie("user_id", str(user['id']))
                        next_url = self.get_argument('next', '/')
                        rsp.update({'code': 200, 'url': next_url})
                    else:
                        rsp['msg'] = 'name and password not matched'
                else:
                    max_id = int(self.db.hsize('user_info'))
                    if max_id == 0:
                        # reg
                        new_id = 1
                        name_lower = name.lower()[:20]
                        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                        nt = int(time())
                        x_real_ip = self.request.headers.get("X-Real-IP")
                        remote_ip = x_real_ip or self.request.remote_ip

                        user = {
                            'id': new_id,
                            'group_id': 1,
                            'name': name,
                            'password': hashed,
                            'reg_time': nt,
                            'reg_ip': remote_ip,
                            'add_by': new_id,
                        }

                        self.db.hset('user_info', new_id, json.dumps(user))
                        self.db.hset('user_name2id', name_lower, new_id)
                        self.db.zset('user_reg_time', new_id, nt)  # time line
                        self.db.zset('user_group:1', new_id, nt)

                        self.set_secure_cookie("user_id", str(user['id']))
                        next_url = self.get_argument('next', '/')
                        rsp.update({'code': 200, 'url': next_url})
                    else:
                        rsp['msg'] = 'name not exist'
            else:
                rsp['msg'] = 'name contain a-z0-9_'
        else:
            rsp['msg'] = 'Please input name and password'

        self.write_json(rsp)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user_id')
        if self.referer:
            self.redirect(self.referer)
            return
        self.redirect('/')
