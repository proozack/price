import uuid
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask_restful import Resource
from flask import current_app, g
from flask import session, request
from flask_restful import abort, reqparse
from flask_login import (current_user)
from app import db
from app.utils.pass_util import hash_password, verify_password
from app.utils.resource import PrivateResource
from flask import render_template,  make_response
import datetime
import time
from app.modules.ims.models import User, AuthLog
from app.utils.local_type import MenuLink
from app.utils.url_utils import UrlUtils
from sqlalchemy import desc, func
from app.modules.price.models import Shop, MetaCategory, Category, EntryPoint
from app.modules.price.models import Ofert, Image
# from sqlalchemy.sql.expression import func

import logging
log = logging.getLogger(__name__)
# MenuLink = namedtuple('MenuLink', ['name', 'representation', 'parent'])


menu = {
    'Woman': {
        'Underwear': [
            MenuLink('Teddies & Bodysuits', 'bodysuits', 'Underwear'),
            MenuLink('Babydolls', 'babydolls',  'Underwear'),
            MenuLink('Matching Sets & Garters', 'garters', 'Underwear'),
            MenuLink('Corsets & Bustiers', 'corsets', 'Underwear'),
            MenuLink('Kimonos', 'kimonos', 'Underwear'),
            MenuLink('Slips', 'slips', 'Underwear'),
            MenuLink('Cami Sets', 'cami_sets', 'Underwear'),
            MenuLink('Shapewear', 'shapewear', 'Underwear'),
        ],
        'Clothes': [],
        'Coats': [],
        'Shoes': [],
    }
}


class HelloWorld(Resource):
    def get(self):
        now = datetime.datetime.now()
        # session['redis_test'] = 'This is a session variable.'
        # return {'hello': 'world'}
        template = render_template(
            'index.html',
            resource={
                'title': 'Price - reale value',
                'icon_path': 'http://2py.eu/img/brand/wtmlogo.png',
                'description': 'Friendly prices search engine',
                'real_url': 'http://2py.eu:9999/api_v1/',
                'static_url': 'http://2py.eu:9080/',
                'year': now.year
            },
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class Shops(Resource):
    def post(self, name):
        if name:
            shop = Shop(name, 1)
            db.session.add(shop)
            db.session.commit()


class MetaCategorys(Resource):
    def post(self, name):
        if name:
            shop = MetaCategory(name, 1)
            db.session.add(shop)
            db.session.commit()


class Categorys(Resource):
    def post(self, name, meta_category_id):
        if name:
            shop = Category(name, meta_category_id, 1)
            db.session.add(shop)
            db.session.commit()


class EntyPoints(Resource):
    def post(self, url, category_id, shop_id):
        if url:
            ep = EntryPoint(url, category_id, shop_id, 1)
            db.session.add(ep)
            db.session.commit()


class CategoryView(Resource):
    def get(self, category, page=1):
        count = 0
        # log.info('Wyświetlam stronę: %r', page)
        # import base64 as b
        # log.info('To jest db %r', dir(db))
        if category == 'bodysuits':
            result = db.session.query(func.max(Ofert.creation_date)).first()
            # o = Ofert.query.filter(Ofert.creation_date >= result[0].date()).join(Image, Image.image == Ofert.image)\
            log.info('Szukam dla daty {}'.format(result))
            if result[0]:
                o = db.session.query(
                    Ofert.title,
                    Ofert.image,
                    Ofert.price,
                    Ofert.currency,
                    Image.control_sum,
                ).join(Image, Image.image == Ofert.image).filter(
                    Ofert.creation_date >= result[0].date()
                ).order_by(
                    Ofert.price.desc()
                )
                count = o.count()
                wyn = o.paginate(page, 32)
            else:
                count = 0
                wyn = {}
            log.info('To jest wyn : %r', wyn)
            if wyn:
                entit = [
                    {
                        'title': getattr(i, 'title'),
                        'image':  i.image,
                        'price': i.price,
                        'currency': i.currency,
                        'hash': i.control_sum,
                    }
                    for i in wyn.items
                ]
            else:
                entit = []
            entities = entit
            """
            entities = []
            for i in entit:
                i['hash'] = b.encodebytes(str.encode(i.get('url'))).decode("utf-8")
                entities.append(i)
                log.info('\n\nTo jest i: %r', i)
            """
        else:
            result = []
            entities = []

        template = render_template(
            'category.html',
            resource={
                'title': '2py.eu',
                'icon_path': 'http://2py.eu/img/brand/wtmlogo.png',
                'description': 'Selected category: {}'.format(category),
                'real_url': 'http://2py.eu:9999/api_v1/',
                'static_url': 'http://2py.eu:9080/',
                'scan_date': result,
                'menu': menu,
                'category': category,
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=entities
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        # log.info('To jest wynik %r', menu)
        log.info('to są entities: %r', entities)
        return resp


class ProductView(Resource):
    def get(self, category, product):
        count = 0
        page = 1
        result = None
        entities = []
        # import base64 as b
        # from app.modules.ims.models import Ofert
        # wyn = b.decodebytes(str.encode(product)).decode("utf-8")
        # from app.modules.ims.models import Ofert, Image
        wyn = product
        """
        # result = db.session.query(func.max(Ofert.creation_date)).first()
        o = Ofert.query.filter(Ofert.url == wyn).order_by(Ofert.creation_date.desc()).all()
        entities = [
            i.get_dict()
            for i in o
        ]
        """
        u = UrlUtils()
        # result = db.session.query(func.max(Ofert.creation_date)).first()
        # o = Ofert.query.filter(Ofert.creation_date >= result[1].date()).join(Image, Image.image == Ofert.image)
        o = db.session.query(
            Ofert.title,
            Ofert.url,
            Ofert.image,
            func.count(Ofert.id).label('count_visit'),
            func.max(Ofert.price).label('max_price'),
            func.avg(Ofert.price).label('avg_price'),
            func.min(Ofert.price).label('min_price'),
            func.max(Ofert.creation_date).label('recent_visits_data'),
            Ofert.currency,
            Image.control_sum,
        ).join(
            Image,
            Image.image == Ofert.image
        ).filter(
            Image.control_sum == wyn
        ).order_by(
            desc(Ofert.title)
        ).group_by(
            Ofert.title,
            Ofert.url,
            Ofert.image,
            Ofert.currency,
            Image.control_sum
        ).all()
        entities = [
            {
                'title': i.title,
                'url': i.url,
                'domain': u.get_domain(i.url),
                'image':  i.image,
                'max_price': i.max_price,
                'avg_price': i.avg_price,
                'min_price': i.min_price,
                'count_visit': i.count_visit,
                'recent_visits_data': i.recent_visits_data,
                'currency': i.currency,
                'hash': i.control_sum,
            }
            for i in o
        ]
        log.info('Ro jest wyn %r', entities)

        template = render_template(
            'product.html',
            resource={
                'title': '2py.eu',
                'icon_path': 'http://2py.eu/img/brand/wtmlogo.png',
                'description': 'Selected product: {}'.format(category),
                'real_url': 'http://2py.eu:9999/api_v1/',
                'static_url': 'http://2py.eu:9080/',
                'scan_date': result,
                'menu': menu,
                'category': category,
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=entities
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        log.info('To jest wynik %r', menu)
        return resp


class Users(Resource):
    def get(self):
        log.info(str(session['redis_test']))
        u = User.query.all()
        lista = [
            {
                'id': i.id,
                'avatar': i.avatar,
                'user_name': i.user_name,
                'email': i.email,
            }
            for i in u
        ]
        return lista

    def post(self):
        u = User('Grzegorz', 'prunio@o2.pl')
        db.session.add(u)
        db.session.commit()


class UserEP(Resource):
    def get(self, ident):
        u = User
        u = u.query.filter(u.id == ident).one_or_none()
        log.info('Get date from objetc: %r', u)
        if u is None:
            return False
        else:
            return {
                'id': u.id,
                'user_name': u.user_name,
                'email': u.email,
                'active': u.active,
            }


class Status(Resource):
    def patch(self, ident, status):
        user = User.query.filter_by(id=ident).first()
        log.info('Zmieniam status użytkownika %r na %r ', user, status)
        user.active = status

        try:
            db.session.commit()
            return True
        except:  # noqa: E722
            log.warn('Błąd aktualizacji', exc_info=True)
            return False


class SignUp(Resource):
    def get(self):
        session['user_name'] = 'proozack'
        session['ident'] = 5
        return True


class SignIn(Resource):
    def get(self):
        session['user_name'] = 'proozack'
        session['ident'] = 5
        # resp = make_response()
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        return True

    def post(self):
        # time.sleep(15)
        try:
            post_parser = reqparse.RequestParser()
            post_parser.add_argument('username', required=False, trim=True, nullable=False)
            post_parser.add_argument('password', required=False, trim=True, nullable=False)
            post_parser.add_argument('email', required=False, trim=True, nullable=False)
            args = post_parser.parse_args()
            u = User(args.get('username'), args.get('email'), hash_password(args.get('password')))
            # u.passwd = hash_password(args.get('password'))
            db.session.add(u)
            db.session.commit()
            # args.get('password')
            # user_name = request.form['user_name']
            log.info('To jest przeslane info %r', args)
            return {
                'status': 'ok',
                'title': 'Add user',
                'message': 'User has added',
            }
        except Exception as e:
            log.error('błąd', exc_info=True)
            return {
                'status': 'error',
                'title': 'User exists',
                'message': 'User already exists',
                'sys_msg': e.args,
            }


class LogOut(Resource):
    def delete(self, session_id):
        """
        log.info('Usuwam sesję użytkownika %s', session_id)
        logout_user()
        session.clear()
        return True
        """
        u"""Zakończenie sesji użytkownika.

        Nie inwaliduje w żaden sposób tokena, ale może odnotować w logach
        audytowych fakt wylogowania użytkownika."""
        if session_id != g.auth_session_id:
            log.debug(
                'Niezgodnosc session_id w naglowku (%s) i w parametrze (%s)',
                g.auth_session_id,
                session_id,
            )
            abort(403)
        # flask_session.clear()
        log.debug('Wylogowanie uzytkownika w sesji %s', g.auth_session_id)


class Auth(Resource):
    def post(self):
        try:
            post_parser = reqparse.RequestParser()
            post_parser.add_argument('login', required=False, trim=True, nullable=False)
            post_parser.add_argument('haslo', required=False, trim=True, nullable=False)
            args = post_parser.parse_args()
            log.info('Autoryzacja użytkownika: [%s]', args.get('login'),)
            if current_user.is_authenticated:
                return {
                    'status': 'redirect',
                    'reason': 'current user is authenticated'
                }
            u = User
            u = u.query.filter(u.user_name == args.get('login')).first()
            a = None
            if u is None or not u.passwd == args.get('haslo'):
                if not verify_password(u.passwd, args.get('haslo')):
                    u = AuthLog(args.get('login'), False, 'Invalid username or password')
                    log.info('Dodaie wpisu %r', u)
                    db.session.add(a)
                    db.session.commit()
                    return {
                        'status': 'rejected',
                        'title': 'Login incorrect',
                        'message': 'Invalid username or password'
                    }
            # login_user(u)
            session_id = uuid.uuid4().hex
            auth_token = Serializer(current_app.config['SECRET_KEY']).dumps({
                'ct': time.time(),  # timestamp - czas wygenerowania
                'vi': 10*60,  # current_app.config['AUTH_TOKEN_TTL_SECONDS'],  # liczba sekund - czas waznosci
                's': session_id,  # id sesji, glownie na potrzeby logow
                'gn': 'Grześ',  # user['imie'],  # imie pracownika
                'sn': 'Prus',  # user['nazwisko'],  # nazwisko pracownika
                'l': 'proozack',  # user['login'],  # nazwa uzytkownika zalogowanego pracownika
                'k': 1,  # id_usr_kollecto,  # id uzytkownika w kollecto
                'p': 'abz',  # self._kody_uprawnien_uzytkownika(user),  # uprawnienia
            })
            a = AuthLog(args.get('login'), True, auth_token)
            log.info('Dodaie wpisu %r', a)
            db.session.add(a)
            db.session.commit()
            return {
                'status': 'ok',
                'session_id': session_id,
                'auth_token': auth_token,
                'zespol': 'Eos',  # InformacjeOZespolePy().get(id_usr_kollecto=id_usr_kollecto)['zespol'],
                'title': 'OK',
                'message': 'login correct',
            }
        except Exception as e:
            log.error('błąd', exc_info=True)
            return {
                'status': 'error',
                'title': 'Backend Error',
                'message': e.args,
                'sys_msg': e.args,
            }


class UiRouterNavigation(PrivateResource):

    def post(self):
        data = request.get_json()
        from_path = (data.get('from') or {}).get('path')
        to_path = (data.get('to') or {}).get('path')
        log.info(
            'Nowa nawigacja w gui; parametry=%r',
            data,
            extra={'from_path': from_path, 'to_path': to_path},
        )
        return {}


class OfertList(PrivateResource):

    def get(self):
        # from app.modules.ims.models import Ofert
        o = Ofert.query.all()
        lista = [
            i.get_dict()
            for i in o
        ]
        return lista
