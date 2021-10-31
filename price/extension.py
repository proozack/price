from celery import Celery
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from .utils import restful_error_messages

import logging
log = logging.getLogger(__name__)

# api = Api(prefix='/api_v1', catch_all_404s=True, errors=restful_error_messages.errors)

cors_expose_headers = [
    'X-Komunikaty-Rsp',
]
cors = CORS(
    # app,
    origins='*', 
    supports_credentials=True, 
    expose_headers=cors_expose_headers
)
# cors = CORS(origins='*', supports_credentials=True, expose_headers=cors_expose_headers)
api = Api(catch_all_404s=True, errors=restful_error_messages.errors)
db = SQLAlchemy()

ma = Marshmallow()
celery_app = Celery()

# celery_app = Celery('tasks', broker='redis://192.168.254.201:6379/0')
# celery_app.conf.result_backend = 'redis://192.168.254.201:6379/1'
