# -*- coding: utf-8 -*-

from .default import Config


class ProductionConfig(Config):
    # application config
    DEBUG_MODE = False
    GZIP = False
    XHEADERS = True

