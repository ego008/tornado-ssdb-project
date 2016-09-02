# -*- coding: utf-8 -*-

from .ssdb_008 import Client

from config import CONFIG

ssdb_main_client = Client(**CONFIG.SSDB_MAIN_DB)  # host='127.0.0.1', port=8686
