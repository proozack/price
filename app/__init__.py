import simplejson
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask import make_response
from .utils import restful_error_messages

import logging
log = logging.getLogger(__name__)
# logging.getLogger('flask_cors').level = logging.DEBUG

from conf.localconfig import Config

db = SQLAlchemy()
login_manager = LoginManager()
api = Api(prefix='/api_v1', catch_all_404s=True, errors=restful_error_messages.errors)

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    # SESSION_TYPE = 'redis'
    # session = Session(app)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    # session.init_app(app)
    cors_expose_headers = [
        'X-Komunikaty-Rsp',
    ]
    cors = CORS(
        app,
        origins='*', 
        supports_credentials=True, 
        expose_headers=cors_expose_headers
    )

    with app.app_context():
        app.secret_key = 'some secret key'
        ma = Marshmallow(app)
        from app.modules.ims import routes
        # Create Database Models
        db.create_all()
        api.init_app(app)
        migrate = Migrate(app, db)
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
