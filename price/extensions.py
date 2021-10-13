import datetime
import logging
import textwrap

from flask import _app_ctx_stack, current_app, make_response
from sqlalchemy import orm
from sqlalchemy.event.api import listen as sqla_listen
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.scoping import instrument
from sqlalchemy.schema import CreateTable

import simplejson
from celery import Celery
from flask_cors import CORS
# from flask_elasticsearch import FlaskElasticsearch
from flask_marshmallow import Marshmallow
# from flask_redis import FlaskRedis
from flask_restful import Api
# from flask_socketio import SocketIO
from flask_sqlalchemy import SignallingSession, SQLAlchemy
# from healthcheck import HealthCheck
from .utils import restful_error_messages
# from util.ldap_user_directory import LDAPUserDirectory
# from windar_api.util.signals import save_procedure_signal
# from .flask_session import Session
# from .flask_statsd import Statsd

log = logging.getLogger(__name__)

"""
@compiles(CreateTable, 'oracle')
def _add_suffixes(element, compiler, **kw):
    text = compiler.visit_create_table(element, **kw)
    if 'oracle_partition' in element.element.info:
        text += textwrap.dedent(element.element.info['oracle_partition']).strip()
    return text

"""
class MySQLASession(SignallingSession):
    my_public_methods = ('execute_with_trace', 'zlec_celery_po_commit')

    def __init__(self, *args, **kwargs):
        super(MySQLASession, self).__init__(*args, **kwargs)
        sqla_listen(self, 'after_commit', self._after_commit)
        sqla_listen(self, 'after_rollback', self._after_rollback)

    def _after_commit(self, session):
        lst = getattr(self, '_zlec_celery_po_commit', None)
        if lst:
            for signature, fmt_opis, kwargs in lst:
                try:
                    log.info('session.after_commit wykonuje zlecenie celery %s', signature)
                    if kwargs:
                        task_ret = signature.apply_async(**kwargs)
                    else:
                        task_ret = signature.delay()
                except Exception:
                    log.error('Blad zlecania zadania celery %s w session.after_commit', signature, exc_info=True)
                else:
                    if not fmt_opis:
                        fmt_opis = 'Zlecilem zadanie celery %s; task_id=%%s' % signature
                    log.info(fmt_opis, task_ret.task_id)
            self._zlec_celery_po_commit = []

    def _after_rollback(self, session):
        lst = getattr(self, '_zlec_celery_po_commit', None)
        if lst:
            for signature, fmt_opis, kwargs in lst:
                log.info('session.after_rollback usuwam z kolejki zlecenie celery %s', signature)
            self._zlec_celery_po_commit = []

    def zlec_celery_po_commit(self, signature, fmt_opis=None, **kwargs):
        lst = getattr(self, '_zlec_celery_po_commit', None)
        if not lst:
            lst = []
        lst.append((signature, fmt_opis, kwargs))
        self._zlec_celery_po_commit = lst

    def execute_with_trace(self, clause, params=None, mapper=None, bind=None, **kw):
        start_date = datetime.datetime.now()
        result = self.execute(clause, params, mapper, bind, **kw)
        end_date = datetime.datetime.now()
        bind = bind if bind else self.get_bind()
        save_procedure_signal.send(start_date=start_date, end_date=end_date, clause=clause, params=params, bind=bind)
        return result

class MyScopedSession(scoped_session):
    pass


# Assign methods from MySession to MyScoppedSession
for meth in MySQLASession.my_public_methods:
    setattr(MyScopedSession, meth, instrument(meth))

class MySQLAlchemy(SQLAlchemy):
    def __init__(self, wymuszony_bind=None):
        self._wymuszony_bind = wymuszony_bind
        super(MySQLAlchemy, self).__init__()

    def apply_driver_hacks(self, app, info, options):
        super(MySQLAlchemy, self).apply_driver_hacks(app, info, options)
        # coerce_to_decimal i coerce_to_unicode nie daja zadnych efektow podczas reflection...
        # wiec nie przekazuje ich do engine
#        if info.drivername.startswith('oracle'):
#            log.info('Przekazuje do sqla engine parametry oraclowe')
#            options['coerce_to_decimal'] = True
#            options['coerce_to_unicode'] = True

    def create_session(self, options):
        return orm.sessionmaker(class_=MySQLASession, db=self, **options)

    def create_scoped_session(self, options=None):
        if options is None:
            options = {}
        scopefunc = options.pop('scopefunc', _app_ctx_stack.__ident_func__)
        options.setdefault('query_cls', self.Query)
        return MyScopedSession(self.create_session(options), scopefunc=scopefunc)

    def execute_with_auto_bind(self, *args, **kwargs):
        if kwargs.get('bind'):
            raise Exception(u'Nie możesz podawać bind')
        kwargs.update({
            'bind': self.get_engine(current_app, self._wymuszony_bind)
        })
        return self.session.execute(*args, **kwargs)

    def execute_with_auto_bind_and_trace(self, *args, **kwargs):
        if kwargs.get('bind'):
            raise Exception(u'Nie możesz podawać bind')
        kwargs.update({
            'bind': self.get_engine(current_app, self._wymuszony_bind)
        })
        return self.session.execute_with_trace(*args, **kwargs)

    def __repr__(self):
        return '<MySQLAlchemy engine=%r>' % self.engine


cors_expose_headers = [
    'X-Komunikaty-Rsp',
]

"""
def apply_kwargs(self, kwargs):
    for key, value in kwargs.items():
        setattr(self, key, value)
    return self
"""

# cors = CORS(origins='*', supports_credentials=True, expose_headers=cors_expose_headers)
api = Api(prefix='/api_v1', catch_all_404s=True, errors=restful_error_messages.errors)
# ldap_user_dir = LDAPUserDirectory()
logger = logging.getLogger('windar_api')
db = MySQLAlchemy()
# db_kanc = MySQLAlchemy('kollecto_kanc')
# db_kplus = MySQLAlchemy('kplus')

# db.Model.apply_kwargs = db_kanc.Model.apply_kwargs = db_kplus.Model.apply_kwargs = apply_kwargs

# ma = Marshmallow()
# statsd = Statsd()
# redis_store = FlaskRedis()
# redis_bpmn_data_engine = FlaskRedis(config_prefix='REDIS_BPMN_DATA_ENGINE')
# redis_multidluznik_data = FlaskRedis(config_prefix='REDIS_MULTIDLUZNIK_DATA')
# redis_requests_meta = FlaskRedis(config_prefix='REDIS_REQUESTS_META')
# es = FlaskElasticsearch()
celery_app = Celery()
# sess = Session()
# socketio = SocketIO()
# health_check = HealthCheck()

"""
@api.representation('application/json')
def output_json(data, code, headers=None):
    # uzywam simplejson zamiast standardowej biblioteki json bo dzieki temu namedtuple sa traktowane
    # tak jak slowniki podczas zamiany z py na json - standardowa biblioteka traktuje je jak tuple
    # i nie pozwala tego nadpisać
    from .util.json_util import _default_write_handler
    resp = make_response(simplejson.dumps(data, default=_default_write_handler, use_decimal=False), code)
    resp.headers.extend(headers or {})
    return resp
"""
