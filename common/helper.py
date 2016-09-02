# -*- coding: utf-8 -*-

import logging
import os
import re
from itertools import izip_longest
import string
import random

user_name_reg = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{3,20}$')


def match_user_name(text):
    return user_name_reg.match(text.encode())


def random_str(n=8):
    allow = list(string.uppercase + string.digits)
    r = []
    for i in range(n):
        r.append(random.choice(allow))
    return ''.join(r)
    # return ''.join(random.sample(allow, n))


# 处理ssdb_008.py 接口返回的较原始的数据


def get_kv_list_keys(kv_list):
    # ['k4', 'v4', 'k1', 'v1', 'k2', 'v2', 'k3', 'v3'] -> ['k4', 'k1', 'k2', 'k3']
    return [kv_list[j] for j in xrange(0, len(kv_list), 2)]


def get_kv_list_values(kv_list):
    # ['k4', 'v4', 'k1', 'v1', 'k2', 'v2', 'k3', 'v3'] -> ['v4', 'v1', 'v2', 'v3']
    return [kv_list[j] for j in xrange(1, len(kv_list), 2)]


def get_kv_list_dict(kv_list):
    # ['k4', 'v4', 'k1', 'v1', 'k2', 'v2', 'k3', 'v3'] -> {'k3': 'v3', 'k2': 'v2', 'k1': 'v1', 'k4': 'v4'}
    return dict(izip_longest(*[iter(kv_list)] * 2, fillvalue=None))
