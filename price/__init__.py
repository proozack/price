import simplejson
# from flask import Flask
from flask_login import LoginManager
from flask import Flask, g, jsonify, request # noqa F401

from flask_session import Session # noqa F401
from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Api
# from flask_marshmallow import Marshmallow
# from flask_cors import CORS
from flask import make_response

from sqlalchemy import create_engine # noqa  F401
from sqlalchemy.orm import sessionmaker # noqa F401

from price.extension import (api, celery_app, db)
# from conf.localconfig import Config
from price import all_tasks # noqa F401


import logging
log = logging.getLogger(__name__)

basestring = str
login_managerte_app = LoginManager()
# jeśli będzie vue.js to poniżej
# api = Api(prefix='/api_v1', catch_all_404s=True, errors=restful_error_messages.errors)
# Wypadku templetingu poniżej
# api = Api(catch_all_404s=True, errors=restful_error_messages.errors)


def create_app(config=None):
    """Construct the core application."""
    # app = Flask(__name__, instance_relative_config=False)
    app = Flask(__name__, instance_relative_config=True)

    if isinstance(config, basestring):
        config = import_string(config)() # noqa F821

    # app = Flask('price', instance_relative_config=True)

    # db = SQLAlchemy()
    # SESSION_TYPE = 'redis'
    # session = Session(app)
    app.config.from_object(config)
    app.config["SQLALCHEMY_ECHO"] = False
    db.init_app(app)
    # login_manager.init_app(app)
    # session.init_app(app)
    """
    cors_expose_headers = [
        'X-Komunikaty-Rsp',
    ]
    cors = CORS(
        app,
        origins='*',
        supports_credentials=True,
        expose_headers=cors_expose_headers
    )
    """
    # SqlAlchemy Session
    # sqlalchemy_engine = create_engine(getattr(Config, 'SQLALCHEMY_DATABASE_URI'))
    # Session = sessionmaker(bind=sqlalchemy_engine)
    # session = Session()

    with app.app_context():
        #  app = Flask('price', instance_relative_config=True)
        app.secret_key = 'some secret key'
        api.app = app
        # ma = Marshmallow(app)

        from price import routes # noqa F401

        from .celery_base_task import mk_base_task
        celery_app.config_from_object(app.config['CELERY'])
        celery_app.Task = mk_base_task(app)

        # from price.modules.ims import routes
        # api.add_resource(HelloWorld, '/')
        # celery_app.config_from_object(app.config.get('CELERY'))
        # Create Database Models
        #
        # https://blog.miguelgrinberg.com/post/using-celery-with-flask
        # https://stackoverflow-com.translate.goog/questions/12044776/how-to-use-flask-sqlalchemy-in-a-celery-task?_x_tr_sl=en&_x_tr_tl=pl&_x_tr_hl=pl&_x_tr_pto=nui
        # https://stackoverflow.com/questions/12044776/how-to-use-flask-sqlalchemy-in-a-celery-task
        #
        # celery_app.init_app(app)
        db.create_all()
        # log.info('Db: \n\n\n%r', dir(db.metadata.tables.items()))
        api.init_app(app)
        migrate = Migrate(app, db) # noqa %841
        app.config["SQLALCHEMY_ECHO"] = False
        return app


@api.representation('application/json')
def output_json(data, code, headers=None):
    # uzywam simplejson zamiast standardowej biblioteki json bo dzieki temu namedtuple sa traktowane
    # tak jak slowniki podczas zamiany z py na json - standardowa biblioteka traktuje je jak tuple
    # i nie pozwala tego nadpisać
    from .utils.json_util import _default_write_handler
    resp = make_response(simplejson.dumps(data, default=_default_write_handler, use_decimal=False), code)
    resp.headers.extend(headers or {})
    return resp
