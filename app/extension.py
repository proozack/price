from celery import Celery
from flask_restful import Api

api = Api(prefix='/api_v1', catch_all_404s=True, errors=restful_error_messages.errors)
celery_app = Celery()
