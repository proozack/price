u"""Moduł zawiera klasy bazowe dla wszystkich zasobów udostępnianych
przez API Windar."""


import logging
import time
import base64
from functools import wraps

from flask import current_app, g, request

from decorator import decorator
from flask_restful import Resource, abort, marshal
from itsdangerous import JSONWebSignatureSerializer as Serializer
from .marshal_tools import marshal_fields_for_sqla_model
from .variabledecode import variable_decode

log = logging.getLogger(__name__)


def str_bool(s):
    if not s:
        return False
    s2 = s.lower()
    if s2 in ('true', 'yes', 'y', 'tak', 't', '1'):
        return True
    if s2 in ('false', 'no', 'nie', 'n', 'f', '0'):
        return False
    raise Exception(u'Niedozwolowa wartosc typu str_bool: %r' % s)


class PublicResource(Resource):
    u"""Klasa bazowa dla zasobów nie wymagających dostarczenia
    tokena potwierdzającego tożsamość użytkownika."""

    pass


class AuthUser(object):
    u"""Podstawowe dane zalogowanego użytkownika."""

    def __init__(self, gn, sn, l, k, p, **kwargs):
        self.imie = gn
        self.nazwisko = sn
        self.login = l
        self.id_uzytkownika_kollecto = k
        self.kody_rol = p

    def ma_role(self, rola):
        return rola.code in self.kody_rol

    def ma_ktoras_z_rol(self, *role):
        kody_rol = self.kody_rol
        for rola in role:
            if rola.code in kody_rol:
                return True
        return False


def user_from_jwt(func):
    u"""Dekorator walidujący token JWT z requesta.

    Token JWT pobieramy z nagłówka `Authorization` lub w pryzpadku jego
    braku z nagłówka `X-Bearer-Token` zgodnego ze standardowym formatem
    autoryzacji Basic. W miejscu nazwy użytkownika zapisany jest
    identyfikator sesji a token w miejscu nazwy użytkownika.

    Identyfikator sesji użytkownika zapisany w tokenie jest porównywany
    z wartością znalezioną w nagłówku.

    Weryfikowany jest dopuszczalny czas życia tokena, porównywany
    z wartością parametru `AUTH_TOKEN_TTL_SECONDS` w konfiguracji aplikacji.

    Wartość identyfikatora sesji zapamiętywana jest w polu `g.auth_session_id`.

    Zawartość tokena (słownik) zapamiętywana jest w polu `g.auth_token_data`.

    Podstawowe dane zalogowanego użytkownika (obiekt klasy `AuthUser`)
    zapamętywane są w polu `g.auth_user`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        def _get_token_from_socket(r):
            if hasattr(r, 'event'):
                e = r.event.get('args')
                if e:
                    return e[0].get('token')
            return

        auth_hdr = request.headers.get('Authorization')
        auth_hdr = auth_hdr or request.headers.get('X-Bearer-Token')
        auth_hdr = auth_hdr or request.args.get('x-bearer-token')
        auth_hdr = auth_hdr or _get_token_from_socket(request)
        if not auth_hdr:
            log.debug('Brak naglowka Authorization')
            abort(401)
        try:
            secret_key = current_app.config['SECRET_KEY']
            #decoded_token = auth_hdr.split()[1].decode('base64') #używane w Puthon2
            #Poprawka na Python3.6 - w python3.7 będzie snów stringiem 
            token = auth_hdr.split()[1]
            btoken = bytes(token, 'utf-8')
            decoded_token = base64.b64decode(btoken).decode('utf-8')

            g.auth_session_id, auth_token = decoded_token.split(':')
            g.auth_token_data = Serializer(secret_key).loads(auth_token)
        except Exception:
            log.error(
                'Blad dekodowania auth tokena JWT:: %r',
                auth_hdr,
                exc_info=True,
            )
            abort(401)
        if g.auth_session_id != g.auth_token_data['s']:
            log.debug(
                'Niezgodnosc session_id w naglowku (%s) i w tokenie (%s)',
                g.auth_session_id,
                g.auth_token_data['s'],
            )
            abort(401)
        token_max_ttl = g.auth_token_data.get('vi') or \
            current_app.config['AUTH_TOKEN_TTL_SECONDS']
        g.auth_token_life_seconds = time.time() - g.auth_token_data['ct']
        if g.auth_token_life_seconds >= token_max_ttl:
            log.debug(
                'Auth token w sesji %s wygasl; czas od wygenerowania: %s',
                g.auth_session_id,
                g.auth_token_life_seconds,
            )
            abort(401)
        try:
            g.auth_user = AuthUser(**g.auth_token_data)
        except Exception:
            log.debug('Nie udalo sie utworzyc AuthUser w sesji %s', g.auth_session_id)
            abort(401)
        return func(*args, **kwargs)
    return wrapper


def wymagane_role(*role):
    @decorator
    def wrapper(func, *args, **kwargs):
        if role:
            if not g.auth_user.ma_ktoras_z_rol(*role):
                return dict(message=u'Nie masz uprawnień do tej operacji'), 403
        return func(*args, **kwargs)
    return wrapper


class PrivateResource(Resource):
    u"""Klasa bazowa dla zasobów wymagających dostarczeni tokena
    potwierdzającego tożsamość zalogowanego użytkownika."""

    method_decorators = [user_from_jwt]


def unpack_sqla_data_for_marshal(res_proxy_list):
    import sqlalchemy.util._collections
    if not res_proxy_list:
        return res_proxy_list
    if isinstance(res_proxy_list, list):
        byla_lista = True
    else:
        res_proxy_list = [res_proxy_list]
        byla_lista = False
    if isinstance(res_proxy_list[0], sqlalchemy.util._collections.AbstractKeyedTuple):
        # lista zawiera ResultProxy a marshal sobie z nimi nie radzi - zamieniam je na slowniki
        unpacked_src_data = [
            resproxy._asdict()
            for resproxy in res_proxy_list
        ]
        if byla_lista:
            return unpacked_src_data
        return unpacked_src_data[0]
    if byla_lista:
        return res_proxy_list
    return res_proxy_list[0]


def datatable_sqla(non_dt_field, dflt_schema=None, marshal_data=True):
    @decorator
    def wrapper(func, *args, **kwargs):
        dt_request = request.args.get('dtSSRequest', '').strip().lower() in ('true', 'tak', 't', 'y', 'yes', '1')

        g.dt_params = {
            'dt_request': dt_request,
            'search': None,
            'order': [],
            'columns': [],
            'start': None,
            'length': None,
        }
        if dt_request:
            src_dt_params = variable_decode(request.args)
            g.dt_params.update({
                'search': src_dt_params['search'].strip(),
                'start': int(src_dt_params['start']),
                'length': int(src_dt_params['length']),
                'order': src_dt_params.get('order', None) or [],
                'columns': src_dt_params['columns'],
                'dflt': src_dt_params.get('dflt', {}),
            })
            if dflt_schema is not None and g.dt_params['dflt']:
                result = dflt_schema().load(g.dt_params['dflt'])
                if result.errors:
                    return dict(message=u'Nieprawidłowe parametry wywołania', errors=result.errors), 400
                g.dt_params['dflt'] = result.data

        src_data = func(*args, **kwargs)
        if callable(src_data):
            src_data = src_data()
        if marshal_data:
            if 'marshal_model' in src_data:
                fields = src_data['marshal_model']
            else:
                fields = marshal_fields_for_sqla_model(
                    src_data['sqla_model'],
                    mapa_podobiektow_sqla=src_data.get('marshal_mapa_podobiektow_sqla'),
                )
            if src_data['data'] and isinstance(src_data['data'], list):
                src_data['data'] = unpack_sqla_data_for_marshal(src_data['data'])
            ret_data = marshal(src_data['data'], fields)
        else:
            ret_data = src_data['data']
        if not dt_request:
            return {
                non_dt_field: ret_data,
            }
        return {
            'draw': request.args.get('draw'),
            'recordsTotal': src_data.get('recordsTotal', len(ret_data)),
            'recordsFiltered': src_data.get('recordsFiltered', len(ret_data)),
            'data': ret_data,
            'additionalData': src_data.get('additionalData', {}),
        }
    return wrapper


def with_user_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.auth_user = AuthUser('IT', '', 'IT', 5721, '')
        return func(*args, **kwargs)
    return wrapper


def pobierz_role(string_rol):
    znaki_specialne = {
        'x': 3,
        'y': 4,
        'z': 5,
    }
    lista_rol = []
    ile_znakow = len(string_rol)
    i = a = 0
    while i < ile_znakow:
        znak = string_rol[i:a+1]
        a = i + znaki_specialne.get(znak, 1)
        lista_rol.append(string_rol[i:a])
        i = a
    return lista_rol


def mapuj_role_na_nazwy(lista_rol):
    from windar_api.util.auth_role import rola
    rozwiazane_rol = []
    for r in lista_rol:
        nazwa_roli = rola.wg_kodu.get(r)
        rozwiazane_rol.append(unicode(nazwa_roli.nazwa))
    return rozwiazane_rol
