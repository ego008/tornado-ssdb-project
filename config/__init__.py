# -*- coding: utf-8 -*-

import logging
import os


_env = os.getenv('TN_APP_ENV')
try:
    if _env == 'PRODUCTION':
        from .production import ProductionConfig as CONFIG
        logging.info('Production config loaded.')
    elif _env == 'TEST':
        from .test import TestConfig as CONFIG
        logging.info('Test config loaded.')
    else:
        from .development import DevelopmentConfig as CONFIG
        logging.info('Development config loaded.')
except ImportError:
    logging.warning('Loading config for %s environment failed, use default config instead.', _env or 'unspecified')
    from .default import Config as CONFIG
