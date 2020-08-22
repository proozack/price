import uuid
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask_restful import Resource, Api
from flask import current_app, g, request
from app.modules.ims.models import User, AuthLog
from flask import Flask, session, request
from flask_restful import abort, reqparse, marshal
from flask_login import (current_user, login_user, logout_user)
from conf.localconfig import Config
from app import db
from app.utils.pass_util import hash_password, verify_password
import flask
from app.utils.resource import PrivateResource

#from app import session
#from sqlalchemy import update

import time
# from flask import make_response
import logging
log = logging.getLogger(__name__)


class HelloWorld(Resource):
    def get(self):
        session['redis_test'] = 'This is a session variable.'
        return {'hello': 'world'}


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
        log.info('Get date from objetc: %r',u)
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
        user.active=status

        try:
            db.session.commit()
            return True
        except:
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
        #resp = make_response()
        #resp.headers['Access-Control-Allow-Origin'] = '*'
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
            #u.passwd = hash_password(args.get('password')) 
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
        flask_session.clear()
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
                'vi': 10*60,# current_app.config['AUTH_TOKEN_TTL_SECONDS'],  # liczba sekund - czas waznosci
                's': session_id,  # id sesji, glownie na potrzeby logow
                'gn': 'Grześ', # user['imie'],  # imie pracownika
                'sn': 'Prus', # user['nazwisko'],  # nazwisko pracownika
                'l': 'proozack', # user['login'],  # nazwa uzytkownika zalogowanego pracownika
                'k': 1, # id_usr_kollecto,  # id uzytkownika w kollecto
                'p': 'abz', #self._kody_uprawnien_uzytkownika(user),  # uprawnienia
            })
            a = AuthLog(args.get('login'), True, auth_token)
            log.info('Dodaie wpisu %r', a)
            db.session.add(a)
            db.session.commit()
            return {
                'status': 'ok',
                'session_id': session_id,
                'auth_token': auth_token,
                'zespol': 'Eos', # InformacjeOZespolePy().get(id_usr_kollecto=id_usr_kollecto)['zespol'],
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
        from app.modules.ims.models import Ofert
        o = Ofert.query.all()
        lista = [
            i.get_dict()
            for i in o
        ]
        return lista
