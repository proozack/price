# -*- coding: utf-8 -*-

import logging
import sys


def updated_dct(dct_to_update, dct_src):
    dct_to_update.update(dct_src)
    return dct_to_update


class Config(object):
    DEBUG = False
    TESTING = False

    # to na potrzeby prawidlowej obslugi wyjatkow przez flask-restful
    PROPAGATE_EXCEPTIONS = False

    AUTH_DODATKOWE_UPRAWNIENIA = {}

    SPIFF_EXCEPTION_ON_MISSING_FILE = True

    LOGGING_TO_CONSOLE = True
    LOGGING_TO_FULL_FILE = False
    LOGGING_TO_PROBLEM_FILE = False
    LOGGING_TO_JSON_FILE = False
    LOGGING_JSON_FILE_MAX_BYTES = 250000000
    LOGGING_JSON_FILE_BACKUP_COUNT = 8
    LOGGING_SMTP_HOST = None
    LOGGING_SMTP_TO = None
    LOGGING_SMTP_USER = None
    LOGGING_SMTP_PWD = None
    LOGGING_SMTP_LEVEL = logging.WARN
    LOGGING_SMTP_FROM = 'windar@eos-ksi.pl'
    LOGGING_SMTP_SUBJECT = u'LOG Z WINDAR'
    LOGGING_LOGSTASH_HOST = None
    LOGGING_LOGSTASH_PORT = 12101
    LOGGING_LOGSTASH_TAGS = None
    LOGGING_LOGSTASH_MSG_TYPE = None
    LOGGING_LOGSTASH_GLOBAL_EXTRA = None
    LOGGING_USE_CELERY_FILTER = False

    # uwaga: domyslnie przekierowuje wszystkie maile na bezpieczny adres
    # zeby przypadkiem w test albo dev nie wyslac czegos do klienta czy dluznika
    # na produkcji trzeba to ustawic na False
    EMAIL_REDIRECT_ALL = ['krzysztof.bogus@eos-ksi.pl']

    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_BINDS = {
        'wdr_main_pg': 'sqlite://',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MIN_SEK_POMIEDZY_ZAPISAMI_UGODY = 10 * 60

    CELERY = dict(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='Europe/Warsaw',
        enable_utc=True,
        worker_hijack_root_logger=False,
        task_track_started=True,
    )

    SESSION_TYPE = 'redis'
    PERMANENT_SESSION_LIFETIME = 172800
    SESSION_USE_SIGNER = False
    SESSION_PERMANENT = True

    REDMINE_WIKI_FORMAT = 'textile'

    def logging_config(self):
        filters = ['process_info', 'session_info', 'request_info', 'extra_logging_context']
        if self.LOGGING_USE_CELERY_FILTER:
            filters.append('celery_task_info_filter')
        msg_type = 'windar'
        if self.LOGGING_LOGSTASH_MSG_TYPE:
            msg_type = self.LOGGING_LOGSTASH_MSG_TYPE
        else:
            api_module = getattr(self, 'API_MODULE', None)
            if api_module:
                msg_type = 'windar:%s' % api_module
            else:
                msg_type = 'windar'
        handlers = {}
        if self.LOGGING_SMTP_HOST and self.LOGGING_SMTP_TO:
            handlers['smtp'] = {
                'class': 'logging.handlers.SMTPHandler',
                'mailhost': self.LOGGING_SMTP_HOST,
                'fromaddr': self.LOGGING_SMTP_FROM,
                'toaddrs': self.LOGGING_SMTP_TO,
                'subject': self.LOGGING_SMTP_SUBJECT,
                'credentials': (self.LOGGING_SMTP_USER, self.LOGGING_SMTP_PWD) if self.LOGGING_SMTP_USER else None,
                'formatter': 'wierszowy',
                'level': self.LOGGING_SMTP_LEVEL,
            }
        if self.LOGGING_TO_CONSOLE:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'basic',
            }
        if self.LOGGING_TO_FULL_FILE:
            handlers['full_file'] = {
                'class': 'logging.FileHandler',
                'filename': self.LOGGING_TO_FULL_FILE,
                'formatter': 'basic',
            }
        if self.LOGGING_TO_PROBLEM_FILE:
            handlers['problem_file'] = {
                'class': 'logging.FileHandler',
                'filename': self.LOGGING_TO_FULL_FILE,
                'formatter': 'basic',
                'level': logging.WARN,
            }
        if self.LOGGING_TO_JSON_FILE:
            handlers['json_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': self.LOGGING_TO_JSON_FILE,
                'maxBytes': self.LOGGING_JSON_FILE_MAX_BYTES,
                'backupCount': self.LOGGING_JSON_FILE_BACKUP_COUNT,
                'encoding': 'utf8',
                'formatter': 'json_file',
                'filters': filters,
            }
        if self.LOGGING_LOGSTASH_HOST:
            handlers['logstash'] = {
                'class': 'logstash_async.handler.AsynchronousLogstashHandler',
                'level': logging.DEBUG,
                'host': self.LOGGING_LOGSTASH_HOST,
                'port': self.LOGGING_LOGSTASH_PORT,
                'filters': filters,
                'formatter': 'logstash',
                'database_path': None,
            }
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'process_info': {
                    '()': 'windar_api.util.logging_filters.ProcessInfoFilter',
                },
                'request_info': {
                    '()': 'windar_api.util.logging_filters.RequestInfoFilter',
                },
                'session_info': {
                    '()': 'windar_api.util.logging_filters.SessionInfoFilter',
                },
                'extra_logging_context': {
                    '()': 'windar_api.util.logging_filters.ExtraLoggingContextFilter',
                },
                'celery_task_info_filter': {
                    '()': 'windar_api.util.logging_filters.CeleryTaskInfoFilter',
                },
            },
            'root': {
                'level': logging.DEBUG,
                'handlers': list(handlers),
            },
            'loggers': {
                'windar_api': {
                    'level': logging.DEBUG,
                },
                'statsd.connection': {
                    'level': logging.WARN,
                },
                'statsd.client': {
                    'level': logging.WARN,
                },
                'imapclient.imaplib': {
                    'level': logging.INFO,
                },
            },
            'handlers': handlers,
            'formatters': {
                'basic': {
                    'format': '%(asctime)s [%(thread)d:%(process)d] %(levelname)-8s %(name)-15s %(message)s',
                    'datefmt ': '%Y-%m-%d %H:%M:%S',
                },
                'logstash': {
                    '()': 'windar_api.util.logging_formatters.LogstashFormatter',
                    'message_type': msg_type,
                    'fqdn': False,
                    'tags': self.LOGGING_LOGSTASH_TAGS,
                    'extra_prefix': None,
                    'extra': self.LOGGING_LOGSTASH_GLOBAL_EXTRA,
                },
                'json_file': {
                    '()': 'windar_api.util.logging_formatters.LogstashFormatter',
                    'message_type': msg_type,
                    'fqdn': False,
                    'tags': self.LOGGING_LOGSTASH_TAGS,
                    'extra_prefix': None,
                    'extra': self.LOGGING_LOGSTASH_GLOBAL_EXTRA,
                },
                'wierszowy': {
                    'format': u"""\
Time: %(asctime)s
Thread ID: %(thread)d
Process ID: %(process)d
Process name: %(processName)s
Level: %(levelname)s
Logger name: %(name)s
Path: %(pathname)s:%(lineno)d
Function: %(funcName)s
Message: %(message)s
""",
                    'datefmt ': '%Y-%m-%d %H:%M:%S',
                },
            },
        }

    # flask-restful
    ERROR_404_HELP = False

    # windar
    AUTH_TOKEN_TTL_SECONDS = 3600
    DOWNLOAD_TOKEN_TTL_SECONDS = 60
    INIT_LDAP_USER_DIR = False

    # drukarki
    CUPS_HOST = 'localhost'
    CUPS_PORT = 631

    # kollecto
    ID_DOMYSL_UZYT_KOLLECTO = 40988  # WINDAR
    LOGIN_DOMYSL_UZYT_KOLLECTO = u'WINDAR'

    # linter
    LINTER_URL = None


class DevConfig(Config):
    DEBUG = True

    def logging_config(self):
        base = super(DevConfig, self).logging_config()
        return updated_dct(
            base,
            {
                'loggers': updated_dct(
                    base['loggers'],
                    {
                        'sqlalchemy.engine': {'level': logging.WARN},
                        'amqp': {'level': logging.INFO},
                    },
                )
            }
        )
