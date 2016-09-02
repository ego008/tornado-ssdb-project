# -*- coding: utf-8 -*-

from core.ssdb_client import ssdb_main_client


class FragmentCache(object):
    db = ssdb_main_client
    KEY = 'fragment_cache:%s'

    @classmethod
    def get(cls, key):
        return cls.db.get(cls.KEY % key)

    @classmethod
    def set(cls, key, value, lifetime=0):
        cls.db.set(cls.KEY % key, value, ex=lifetime)
        return True

    @classmethod
    def delete(cls, key):
        return cls.db.delete(cls.KEY % key) == 1

    @classmethod
    def has(cls, key):
        return cls.db.exists(cls.KEY % key)
