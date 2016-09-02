# -*- coding: utf-8 -*-

import json

from core.ssdb_client import ssdb_main_client
from common.helper import get_kv_list_keys, get_kv_list_dict


class User(object):
    db = ssdb_main_client

    @classmethod
    def get_by_email(cls, email):
        user_id = cls.db.hget('user_email2id', email)
        if user_id:
            return User.get_by_id(user_id)

    @classmethod
    def get_by_name(cls, name):
        user_id = cls.db.hget('user_name2id', name)
        if user_id:
            return User.get_by_id(user_id)

    @classmethod
    def get_by_id(cls, user_id):
        value = cls.db.hget('user_info', user_id)
        if value:
            return json.loads(value)

    @classmethod
    def get_by_ids(cls, user_ids=None):
        if not user_ids:
            return {}
        _dict = {}
        kvs = cls.db.multi_hget('user_info', *user_ids)
        for i in range(0, len(kvs), 2):
            _dict[kvs[i]] = json.loads(kvs[i+1])
        return _dict

    @classmethod
    def get_by_keyword(cls, kw=None, limit=20):
        if not kw:
            return []
        tb_name = 'user_info'
        total_num = int(cls.db.hsize(tb_name))
        items = []
        if total_num:
            key_start = ''
            go_on = 1
            kw_lower = kw.lower()
            while go_on:
                kv_list = cls.db.hscan(tb_name, key_start, '', 100)
                if not kv_list:
                    break
                for i in range(0, len(kv_list), 2):
                    key_start = kv_list[i]
                    item = json.loads(kv_list[i + 1])
                    if kw_lower in item['name'].lower():
                        items.append(item)
                        if len(items) > limit:
                            go_on = 0
                            break

        return {'items': items, 'has_next': 0, 'score_start': '', 'total_num': len(items)}

    @classmethod
    def get_item_page(cls, tb_name, score_start, limit=20):
        # tb_name = 'user_reg_time'  # 按新注册顺序
        if score_start:
            try:
                score_start = int(score_start)
            except:
                score_start = ''
        total_num = int(cls.db.zsize(tb_name))
        items = []
        new_score_start = ''
        if total_num:
            kv_list = cls.db.zrscan(tb_name, '', score_start, '', limit + 1)
            if kv_list:
                keys = get_kv_list_keys(kv_list)
                item_dict = get_kv_list_dict(cls.db.multi_hget('user_info', *keys))
                for i in range(0, len(kv_list), 2):
                    tid = kv_list[i]
                    new_score_start = kv_list[i + 1]  # for next page
                    items.append(json.loads(item_dict[tid]))

        return {'items': items[:limit],
                'has_next': 1 if len(items) == limit + 1 else 0,
                'score_start': new_score_start,
                'total_num': total_num}


