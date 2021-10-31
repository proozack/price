import datetime
from datetime import date
import time
import uuid
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask_restful import Resource
from flask import current_app, g
from flask import session, request
from flask_restful import abort, reqparse
from flask import render_template, make_response
from flask_login import (current_user)
from sqlalchemy import desc, func
from price import db
from price.utils.pass_util import hash_password, verify_password
from price.utils.resource import PrivateResource
from price.modules.ims.models import User, AuthLog
from price.utils.local_type import MenuLink
from price.utils.url_utils import UrlUtils
from price.modules.price.models import Shop, MetaCategory, Category, EntryPoint
from price.modules.price.models import Ofert, Image
from price.modules.imp_price.models import ImpCatalogPage 
# from price.extensions import app
# from localconfig import Config
from price.modules.price import db_utils
from price.modules.price.db_utils import ProductDbUtils, TagDbUtils, EntryPointsDbUtils
from price.utils.resource import datatable_sqla
# from sqlalchemy.sql.expression import func

import logging
log = logging.getLogger(__name__)
# MenuLink = namedtuple('MenuLink', ['name', 'representation', 'parent'])

class Config():
    REAL_URL = 'http://py2.eu:7001/'
    STATIC_URL = 'http://py2.eu:7003/'

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

class EntryPoint(Resource):

    def get(self, entry_point_id, page=1):
        now = datetime.datetime.now()
        pdbu = ProductDbUtils()
        epdbu = EntryPointsDbUtils()
        entry_point = epdbu.get_entry_point_by_id(entry_point_id)
        result = None
        count = 1
        o = pdbu.bq_get_unique_oferts(entry_point_id=entry_point_id, create_date=date.today())
        count = o.count()
        wyn = o.paginate(page, 32)
        result = datetime.datetime.now()

        if wyn:
            entit = [
                {
                    'product_id': None,
                    'title': getattr(i, 'title'),
                    'image':  i.image,
                    'count': i.count,
                    'price': i.price,
                    'currency': 'zł',
                    'hash': '',
                    'brand': i.main_brand,
                    'product_url': i.url,
                }
                for i in wyn.items
            ]
        else:
            entit = []

        entities = entit

        ct = db_utils.CategoryDbUtils()
        entities = entit

        template = render_template(
            'entry_point.html',
            resource={
                'title': '2py.eu',
                'description': 'Selected entry point: {}'.format(entry_point.url),
                'icon_path': ''.join([Config.STATIC_URL, 'logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'scan_date': result,
                'menu': menu,
                'category': entry_point.url,
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=entities,
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class Imports(Resource):
    def get(Resource):
        now = datetime.datetime.now()
        ct = db_utils.CategoryDbUtils()
        template = render_template(
            'imports.html',
            resource = {
                'title': 'Imports - reale value',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'description': 'List procesing oferts from catalog',
                'year': now.year,
                'dt_table': [
                    'ID',
                    'Title',
                    'ID entry point',
                    'Name',
                    'Manufacturer',
                    'Cretaion date',
                ]
            },
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class DtImports(Resource):
    def get(self):
        odu = db_utils.OfertDbUtils()
        data = odu.get_all_ofert_by_entry_point(28)
        ile = 1
        return {
            "draw": 1,
            "recordsTotal": ile,
            "recordsFiltered": 57,
            "data": data        
        }

class Tag(Resource):
    def get(self, tag):
        ct = db_utils.CategoryDbUtils()
        tdb = TagDbUtils()
        count = 0
        page = 1
        result = None
        entities = []
        wyn = tag
        u = UrlUtils()
        pdu = db_utils.TagDbUtils()
        o = pdu.get_product_by_tag(tag)
        meaning = tdb.get_meaning_by_tag(tag)
        now = datetime.datetime.now()
        meaning = meaning[0] if meaning[0] else 'Not set'
        entities = [
            {
                'product_id': i.product_id,
                'ofert_id': i.ofert_id,
                'title': i.title,
                'url': i.url,
                'domain': u.get_domain(i.url),
                'image':  i.image,
                'max_price': i.price, # i.max_price,
                'avg_price': None, # i.avg_price,
                'min_price': None, # i.min_price,
                'count_visit': None, # i.count_visit,
                'recent_visits_data': now, # i.recent_visits_data,
                'currency': i.currency,
                'hash': i.control_sum,
                'manufacturer': i.brand_name.capitalize(), # i.manufacturer
                'tags': i.all_tags.split(';'),
                'main_tags':  i.tags.split(';'),
                'category':  i.category,
                'subcategory': i.subcategory,
                'colortags': i.colortags,
            }
            for i in o
        ]
        means_list = [
            { 'label': mens.meaning }
            for mens in pdu.get_list_meaning() 
        ]
        log.info('Resultset %r', means_list)
        template = render_template(
            'tag.html',
            resource={
                'title': '2py.eu',
                'description': 'Selected tag: "{}", meaning: "{}"'.format(tag, meaning),
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'scan_date': result,
                'menu': menu,
                'category': tag,
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1,
                'meaning': means_list,
                'tag': tag,
            },
            entities=entities,
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        log.info('To jest wynik %r', menu)
        return resp

    def post(self, tag):
        log.info('Nadaje znaczenie tagowi %r znaczenie %r', tag, request.values);
        data = request.values
        meaning = data.get('data')
        log.info('Nadaje znaczenie %r', meaning);
        w = db_utils.TagDbUtils()
        w.set_meaning(tag, meaning)
        return True


class Tags(Resource):

    def get(self):
        now = datetime.datetime.now()
        ct = db_utils.CategoryDbUtils()

        config = {
            'title': 'Tags by counting',
            'dt_header': [
                'Tag Id',
                'Tag name',
                'Count'
            ],
            'date': ct.get_category_for_menu() 
        }


        template = render_template(
            'dt.html',
            resource = {
                'title': 'Tags by counting',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'description': 'Tags by counting',
                'year': now.year,
                'dt_table': [
                    'Tag Id',
                    'Tag name',
                    'Meaning',
                    'Count',
                ],
                'dt_config': {
                    'ajax': 'dt_tags',
                }
            },
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class DtTags(Resource):

    @datatable_sqla('tags_list')
    def get(self):
        # log.info('Reqparse: %r', request.args)

        tdu = db_utils.TagDbUtils()
        ile = 1
        return {
            "data": tdu.get_tag_by_counting() 
        }


class Start(Resource):
    def get(self):
        ct = db_utils.CategoryDbUtils()
        now = datetime.datetime.now()
        result = db.session.query(func.max(Ofert.creation_date)).first()
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
        wyn = o.paginate(1, 24)
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

        template = render_template(
            'index.html',
            resource={
                'title': 'Price - reale value',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'description': 'Friendly prices search engine',
                'year': now.year
            },
            entities=entit,
            menu = ct.get_category_for_menu()
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
        pdu = ProductDbUtils()
        ct = db_utils.CategoryDbUtils()
        category_id = ct.get_category_id_by_slug(category)

        count = 0
        """
        result = db.session.query(func.max(Ofert.creation_date)).first()
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
        """
        o = pdu.get_product_for_catgeory_view(category_id)
        count = o.count()
        wyn = o.paginate(page, 32)
        result = datetime.datetime.now()
        if wyn:
            entit = [
                {
                    'product_id': i.product_id,
                    'title': getattr(i, 'title'),
                    'image':  i.image,
                    'count': i.count,
                    'min_price': i.min_price,
                    'max_price': i.max_price,
                    'currency': 'zł',
                    'hash': '',
                    'brand': i.brand
                }
                for i in wyn.items
            ]
        else:
            entit = []

        entities = entit

        template = render_template(
            'category.html',
            resource={
                'title': '2py.eu',
                'description': 'Selected category: {}'.format(category),
                'icon_path': ''.join([Config.STATIC_URL, 'logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'scan_date': result,
                'menu': menu,
                'category': category,
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=entities,
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        # log.info('To jest wynik %r', menu)
        # log.info('to są entities: %r', entities)
        return resp


class ShopsStats(Resource):
    def get(self):
        ct = db_utils.CategoryDbUtils() 
        result = None
        entities = []
        _sql = """
        WITH stat AS (
                SELECT
                        ep.id,
                        ep.shop_id,
                        ep.url,
                        o.creation_date::date AS c_date,
                        COUNT(o.id) as ile
                FROM price_ofert AS o
                JOIN price_entry_point AS ep ON ep.id = o.entry_point_id
                JOIN price_shop AS s ON s.id = ep.shop_id
                WHERE o.creation_date::date > CURRENT_DATE - 4
                GROUP BY ep.id, ep.url, ep.shop_id, o.creation_date::date
        )
        SELECT
                pep.id as ep_id,
                pep.url as entry_point,
                ps.url,
                COALESCE(s3.ile, 0) AS i3,
                COALESCE(s2.ile, 0) AS i2,
                COALESCE(s1.ile, 0) AS i1,
                COALESCE(s0.ile, 0) AS i0,
                CASE
                        WHEN COALESCE(s0.ile, 0) > COALESCE(s1.ile, 0) THEN '↑'
                        WHEN COALESCE(s0.ile, 0) < COALESCE(s1.ile, 0) THEN '↓'
                ELSE
                        '='
                END as dynamic
        FROM price_shop AS ps
        JOIN price_entry_point AS pep ON pep.shop_id = ps.id
        LEFT JOIN stat As s0 ON s0.id = pep.id AND s0.c_date = CURRENT_DATE
        LEFT JOIN stat As s1 ON s1.id = pep.id AND s1.c_date = CURRENT_DATE - 1
        LEFT JOIN stat As s2 ON s2.id = pep.id AND s2.c_date = CURRENT_DATE - 2
        LEFT JOIN stat As s3 ON s3.id = pep.id AND s3.c_date = CURRENT_DATE - 3
        WHERE ps.active = True
        AND ps.deleted = False
        ORDER BY ps.url
        """
        result = db.engine.execute(_sql)

        fields = result.keys()
        entities = [
            {
            field: getattr(i, field) # noqa E122
            for field in fields # noqa E122
            }
            for i in result
        ]
        template = render_template(
            'shops.html',
            resource={
                'title': '2py.eu',
                'description': 'Shops list',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'menu': menu,
                'fields': fields,
                'fields_name': [
                    'Entry point ID',
                    'URL',
                    'Shop url',
                    'T - 3 days',
                    'T - 2 days',
                    'T - 1 day',
                    'Today',
                    'Dynamic',
                ]
            },
            entities=entities,
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        log.info('To jest wynik %r', menu)
        return resp


class ProductView(Resource):
    # def get(self, category, product):
    def get(self, product):
        ct = db_utils.CategoryDbUtils()
        count = 0
        page = 1
        result = None
        entities = []
        wyn = product
        u = UrlUtils()
        pdu = ProductDbUtils()
        o = pdu.get_product_by_product_def_id(wyn)
        tit = pdu.get_product_title_by_id(wyn)
        now = datetime.datetime.now()
        entities = [
            {
                'product_id': i.product_id,
                'ofert_id': i.ofert_id,
                'title': i.title,
                'url': i.url,
                'domain': u.get_domain(i.url),
                'image':  i.image,
                'max_price': i.price, # i.max_price,
                'avg_price': None, # i.avg_price,
                'min_price': None, # i.min_price,
                'count_visit': None, # i.count_visit,
                'recent_visits_data': now, # i.recent_visits_data,
                'currency': i.currency,
                'hash': i.control_sum,
                'manufacturer': i.brand_name.capitalize(), # i.manufacturer
                'tags': i.tags.split(';'),
            }
            for i in o
        ]
        template = render_template(
            'product.html',
            resource={
                'title': '2py.eu',
                'description': '{}'.format(' '.join([tit[1].capitalize(), tit[3].capitalize()])),
                'brand_image': tit[2],
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'scan_date': result,
                'menu': menu,
                'category': 'Dupa',
                'page': page,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=entities,
            menu = ct.get_category_for_menu()
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
        o = Ofert.query.all()
        lista = [
            i.get_dict()
            for i in o
        ]
        return lista

