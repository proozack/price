# -*- coding: utf-8 -*-

import json
import logging
import logging.config
import os
import pprint
import time
# from uuid import uuid4

#import socket
from flask import Flask, g, jsonify, request
from werkzeug.utils import import_string

#from db_meta.ext_db.id_decoder import KonwerterExtDbId
#from extensions import (api, celery_app, cors, db, db_kplus, es, health_check, ldap_user_dir, logger, ma,
#                        redis_bpmn_data_engine, redis_multidluznik_data, redis_requests_meta, redis_store, sess,
#                        socketio, statsd)
from price.extensions import (api, celery_app, db)
# importuje all_tasks zeby byly zaladowane na potrzeby workerow celery
# from tasks import all_tasks  # noqa: F401


#from util import url_converters
#from util.exceptions import ENotImplemented, EWindar, EWindarUser
#from util.global_const import DctApiModules
#from util.request_id import get_request_id_parts

log = logging.getLogger(__name__)
"""
def _init_db_porter(app):
    log.info('Pobieram definicje tabel z bazy Porter')
    import db_meta.porter  # noqa: F401
    from db_meta.porter_util import PorterReflected
    engine_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
    orig_level = engine_logger.level
    engine_logger.setLevel(logging.WARN)
    PorterReflected.prepare(db.get_engine(app, 'porter_main_pg'))
    # db.reflect('porter_main_pg')
    engine_logger.setLevel(orig_level)
    log.info('Koniec pobierania definicji tabel z bazy Porter')
"""

def init_all_db(api, app):
    u"""Moduł all_db powinien importować wszystkie moduły zawierające
    tabele należące do windara - na potrzeby `manage db create_all|drop_all`.
    """
    log.info('Aktywuje tabele sqlalchemy')
    _init_db_kollecto()  # kollecto jako pierwsze zeby tabelki wdr mogly definiowac klucze obce
    import db_meta.auth

def init_modul_ugod_api(api, app):
    log.info('Aktywuje tabele sqlalchemy')
    #_init_db_kollecto()  # kollecto jako pierwsze zeby tabelki wdr mogly definiowac klucze obce
    #if not app.config.get('TESTING'):
    #    _init_db_kollecto_fdw(app)
    import db_meta.magazyn_plikow
    log.info('Rejestruje moduly powiadomien kolejki wydrukow')
    from util.global_const import DctKolejkaWydrukow
    log.info('Rejestruje zasoby')
    from resources.ping import Ping, Diagnostics
    from resources.healthz import Readiness, mk_metrics_resource
    from resources.egzekucje.wnioski_egzekucyjne import UsuwaniePaczekZRaportu
    from resources.stats import PaczkaTimerow
    from resources.inspektorat_terenowy import ZapotrzebowanieIloscioweSpraw

    api.app = app
    if not app.config.get('TESTING'):
        init_health_checks(DctApiModules.UGODY)
        api.add_resource(Ping, '/ping')
        api.add_resource(Diagnostics, '/diagnostics')
        api.add_resource(Readiness, '/healthz/readiness')
        api.add_resource(mk_metrics_resource(DctApiModules.UGODY), '/healthz/metrics')
    sms_ustawienia_grup.SmsUstawieniaGrup.register_with_api(
        api,
        '/it_service_helpers/sms_ustawienia_grup',
    )
    sre.Systemy.register_with_api(
        api,
        '/it_service_helpers/sre/system',
    )


    api.add_resource(
        raporty.GrupyRaportow,
        '/raporty/grupy_raportow',
    )


api_modules = dict(
    modul_ugod=init_modul_ugod_api,
)


def create_app(config=None):
    app = Flask('windar_api', instance_relative_config=True)
    # app.url_map.converters['ext_db_id'] = KonwerterExtDbId
    # app.url_map.converters['date'] = url_converters.KonwerterData
    # app.url_map.converters['signed_int'] = url_converters.SignedIntConverter
    if config is not None:
        if isinstance(config, basestring):
            config = import_string(config)()
        app.config.from_object(config)
        init_logger(app, config.logging_config())
    # logger.info('starting %s' % app.name)
    if app.config.get('INIT_LDAP_USER_DIR'):
        ldap_user_dir.init_app(app)
    # cors.init_app(app)
    if app.config.get('SQLALCHEMY_DATABASE_URI'):
        log.info('Inicjuje sqlalchemy')
        db.init_app(app)
        log.info('Inicjuje sqlalchemy dla kollecto plus')
        # db_kplus.init_app(app)
    #
    # from .celery_base_task import mk_base_task
    # celery_app.config_from_object(app.config['CELERY'])
    # celery_app.Task = mk_base_task(app)
    # from .util import celery_statsd  # noqa: F401  # ten import inicjuje wysylanie danych do statsd
    #
    # statsd.init_app(app)
    # ma.init_app(app)
    api.init_app(app)
    if app.config.get('REDIS_URL'):
        log.info('Inicjuje redis')
        redis_store.init_app(app)
    # if app.config.get('REDIS_BPMN_DATA_ENGINE_URL'):
    #     log.info('Inicjuje redis dla zrodel danych BPMN')
    #     redis_bpmn_data_engine.init_app(app)
    # if app.config.get('REDIS_MULTIDLUZNIK_DATA_URL'):
    #     log.info('Inicjuje redis dla danych multidłużnika')
    #     redis_multidluznik_data.init_app(app)
    # if app.config.get('REDIS_REQUESTS_META_URL'):
    #     log.info('Inicjuje redis dla meta informacji o requestach')
    #     redis_requests_meta.init_app(app)
    # if app.config.get('ELASTICSEARCH_HOST'):
    #     log.info('Inicjuje elasticsearch')
    #     es.init_app(app)
    setattr(app.config, 'SESSION_REDIS_CONN', 'redis://192.168.254.201:6379/2')
    if app.config.get('TESTING'):
        log.info(u'Konfiguracja testowa, inicjuje wszystkie moduły')
        with app.app_context():
            init_all_db(api, app)
            init_sessions_api(api, app)
            init_kollecto_db_api(api, app)
            init_modul_ugod_api(api, app)
            init_workflow_api(api, app)
            # init_modul_porter(api, app)
    else:
        log.error('\n\n\n------ \n%r',app.config)
        if app.config.get('SESSION_REDIS_CONN'):
            import redis
            log.info(u'Inicjuje flask session')
            sess.init_redis(redis.Redis(**app.config['SESSION_REDIS_CONN']))
            sess.init_app(app)
        else:
            raise Exception(u'Nie uzupełniono konfiguracji redisa dla flask_session')

    init_api = api_modules[app.config['API_MODULE']]
    # if app.config.get('SOCKETIO_MESSAGE_QUEUE'):
    #     socketio.init_app(app=None, message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    with app.app_context():
        init_api(api, app)

    # Subscribe to signals
    # from windar_api.util import signals
    # from windar_api.operacje import monitoring
    # signals.save_procedure_signal.connect(monitoring.zapisz_wywolanie_procedury)

    if app.config.get('STORE_USER_LAST_ACTIVITY_TIME', True):
        @app.after_request
        def save_user_activity(response):
            try:
                if hasattr(g, 'auth_user'):
                    id_uzytkownika = g.auth_user.id_uzytkownika_kollecto
                else:
                    id_uzytkownika = None
            except Exception:
                id_uzytkownika = None
            if id_uzytkownika:
                redis_store.zadd('user_last_activity_time', time.time(), id_uzytkownika)
            return response

    # if app.config.get('REDIS_REQUESTS_META_URL'):
    #     from windar_api.operacje.monitoring import (prefix_requests_meta, klucz_requests_in_progress,
    #                                                 klucz_requests_finished)

        @app.before_request
        def add_info_about_request():
            try:
                req_uuid = unicode(uuid4())
                g.redis_request_uuid = req_uuid
                start_time = time.time()
                pipe = redis_requests_meta.pipeline()
                pipe.setex(
                    '%s:%s' % (prefix_requests_meta, req_uuid),
                    time=72 * 60 * 60,
                    value=json.dumps({
                        'st': start_time,
                        're': request.endpoint,
                        'rp': request.path,
                        'rm': request.method.lower(),
                        'ra': request.remote_addr,
                        'h': socket.gethostname(),
                    })
                )
                pipe.zadd(klucz_requests_in_progress, start_time, req_uuid)
                pipe.execute()
            except Exception:
                log.error(u'Błąd zapisania informacji w redis o rozpoczęciu requesta', exc_info=True)

        @app.after_request
        def save_finished_request(response):
            try:
                req_uuid = getattr(g, 'redis_request_uuid', None)
                if not req_uuid:
                    log.warning(u'Nie znaleziono `redis_request_uuid` we `flask.g`')
                else:
                    request_id = get_request_id_parts()
                    auth_user = getattr(g, 'auth_user', None)
                    pipe = redis_requests_meta.pipeline()
                    redis_requests_meta.zrem(klucz_requests_in_progress, req_uuid)
                    redis_requests_meta.lpush(klucz_requests_finished, json.dumps({
                        'ri': req_uuid,
                        'ro': request_id.root_id,
                        'pi': request_id.parent_id,
                        'rs': request_id.request_id,
                        'et': time.time(),
                        'iz': auth_user.id_uzytkownika_kollecto if auth_user else None,
                    }))
                    pipe.execute()
            except Exception:
                log.error(u'Błąd zapisania informacji w redis o zakończeniu requesta', exc_info=True)
            return response

    @app.after_request
    def add_header(response):
        # naglowki kontrolujace cache
        response.cache_control.max_age = 1
        response.cache_control.public = False
        response.cache_control.private = True
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
        # rsp komunikaty
        komunikaty_rsp = getattr(g, 'komunikaty_rsp', None)
        if komunikaty_rsp:
            response.headers['X-Komunikaty-Rsp'] = json.dumps(komunikaty_rsp)
        #
        return response

    @app.errorhandler(Exception)
    def handle_exc(error):
        from .util.exceptions import get_exc_message
        log.exception(error)
        try:
            message = get_exc_message(error)
        except Exception:
            message = u'Nieokreślony błąd'
        response = jsonify({'message': message})
        response.status_code = 500
        return response

    @app.errorhandler(ENotImplemented)
    def handle_exc_not_implemented(error):
        from .util.exceptions import get_exc_message
        log.info(error)
        try:
            message = get_exc_message(error)
        except Exception:
            message = u'Nieokreślony błąd'
        response = jsonify({'message': message})
        response.status_code = 501
        return response

    @app.errorhandler(EWindar)
    def handle_exc_windar(error):
        log.exception(error)
        response = jsonify(error.data)
        response.status_code = error.code
        return response

    @app.errorhandler(EWindarUser)
    def handle_exc_form_info(error):
        log.info('%s: %s' % (error.title, error.description))
        response = jsonify(error.data)
        response.status_code = error.code
        return response

    oczyszczony_env = {}
    for k, v in os.environ.iteritems():
        if 'wdr_sqla_' in k.lower() or 'wdr_ldap_' in k.lower():
            oczyszczony_env[k] = '***'
        else:
            oczyszczony_env[k] = v

    logger.info('environ: %s', pprint.pformat(oczyszczony_env))
    logger.info('started %s' % app.name)
    return app


def init_logger(app, cfg):
    if cfg:
        logging.config.dictConfig(cfg)





"""
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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging
log = logging.getLogger(__name__)
# logging.getLogger('flask_cors').level = logging.DEBUG

from conf.localconfig import Config
log.error(Config)
db = SQLAlchemy()
login_manager = LoginManager()
api = Api(catch_all_404s=True, errors=restful_error_messages.errors)

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    app.config["SQLALCHEMY_ECHO"] = False
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
"""
