# price
A promo gui and api


##### Example localconfig
#### Path: vim conf/localconfig.py

#from sys import stdout
import os
from os import environ
import redis
from logging.handlers import RotatingFileHandler
from datetime import timedelta
import logging
import sys

"""
# If you using many db
databases = {
    'main_db': 'postgresql+psycopg2://user:passsword@host:port/db',
}
"""
class Config(object):
    log = logging.getLogger()
    handler = RotatingFileHandler(
        '/<Path to log file>/log/example.log', 
        maxBytes=1000000, 
        backupCount=5
    )
    std_out_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('[%(asctime)s] %(module)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    std_out_handler.setFormatter(formatter)
    #handler.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    log.addHandler(std_out_handler)




    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@host:port/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # General Config
    #SECRET_KEY = os.urandom(24)#environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Flask-Session
    # @abc1233!@$ --- haslo do redisa

    # SESSION_TYPE = environ.get('SESSION_TYPE')
    #SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))
    # SESSION_REDIS = redis.from_url('redis://redis_pass@localhost:6379/0')
    #SECRET_KEY = os.urandom(24)#environ.get('SECRET_KEY')
    # PERMANENT_SESSION_LIFETIME=timedelta(minutes=5)

    PRICE_USER_ID = 1
