import re
import datetime
from decimal import Decimal
from decorator import decorator
from flask import request, g
import dateutil.parser
from dateutil.tz import tzlocal
from marshmallow import validate, ValidationError, fields, validates_schema
from ..extensions import ma

import logging
log = logging.getLogger(__name__)


def validate_ma(schema):
    @decorator
    def wrap(f, *args, **kwargs):
        if request.values:
            log.debug('%s.load data request.values: %r', schema, request.values)
            result = schema().load(request.values)
        else:
            data = request.get_json()
            log.debug('%s.load data get_json: %r', schema, data)
            result = schema().load(data)
        g.req_para, errors = result.data, result.errors
        log.debug('load result: %s', result)
        if errors:
            return dict(message=u'Nieprawidłowe parametry wywołania', errors=errors), 400
        return f(*args, **kwargs)
    return wrap


def validate_schema(schema, data):
    log.debug('%s.load data: %r', schema, data)
    result = schema().load(data)
    log.debug('load result: %s', result)
    errors = result.errors
    errors = (dict(message=u'Nieprawidłowe parametry wywołania', errors=errors), 400) if errors else None
    return result.data, errors


_D0 = Decimal(0)
_D001 = Decimal('0.01')

_tzlocal = tzlocal()


class DateField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value.strftime('%Y-%m-%d')

    def _deserialize(self, value, attr, data):
        try:
            if isinstance(value, datetime.date):
                return value
            dt = dateutil.parser.parse(value)
            if dt.tzinfo:
                dt = dt.astimezone(_tzlocal)
            return dt.date()
        except Exception:
            log.info('blad', exc_info=True)
            raise ValidationError(u'Nieprawidłowy format daty')


class DateTimeField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def _deserialize(self, value, attr, data):
        try:
            if isinstance(value, datetime.datetime):
                return value
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            log.info('blad', exc_info=True)
            raise ValidationError(u'Nieprawidłowy format daty')


class StringField(fields.String):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, basestring):
            self.fail('invalid')
        value = value.strip() or None
        if value is None and getattr(self, 'allow_none', False) is not True:
            self.fail('required')
        return value


def _cmp_validators(gt=None, ge=None, lt=None, le=None):
    validators = []
    if gt is not None:
        validators.append(lambda v: v > gt)
    if ge is not None:
        validators.append(lambda v: v >= ge)
    if lt is not None:
        validators.append(lambda v: v < lt)
    if le is not None:
        validators.append(lambda v: v <= le)
    return validators


def req_int(gt=None, ge=None, lt=None, le=None):
    validators = _cmp_validators(gt, ge, lt, le)
    return ma.Integer(required=True, validate=validators)


def opt_int(gt=None, ge=None, lt=None, le=None):
    validators = _cmp_validators(gt, ge, lt, le)
    return ma.Integer(allow_none=True, validate=validators, missing=None)


def req_ident():
    validators = []
    return ma.Integer(required=True, validate=validators)


def opt_ident():
    validators = []
    return ma.Integer(allow_none=True, validate=validators, missing=None)


def req_kwota(gt=None, ge=None, lt=None, le=None):
    validators = _cmp_validators(gt, ge, lt, le)
    return ma.Decimal(required=True, validate=validators)


def opt_kwota(gt=None, ge=None, lt=None, le=None):
    validators = _cmp_validators(gt, ge, lt, le)
    return ma.Decimal(allow_none=True, validate=validators, missing=None)


req_prc = req_kwota
opt_prc = opt_kwota


def req_data(gt=None, ge=None, lt=None, le=None):
    validators = []
    return DateField(required=True, validate=validators)


def opt_data(gt=None, ge=None, lt=None, le=None):
    validators = []
    return DateField(allow_none=True, validate=validators, missing=None)


def req_dataczas(gt=None, ge=None, lt=None, le=None):
    validators = []
    return DateTimeField(required=True, validate=validators)


def opt_dataczas(gt=None, ge=None, lt=None, le=None):
    validators = []
    return DateTimeField(allow_none=True, validate=validators, missing=None)


def req_bool():
    validators = []
    return ma.Boolean(required=True, validate=validators)


def opt_bool(missing=None):
    validators = []
    return ma.Boolean(allow_none=True, validate=validators, missing=missing)


def req_str():
    validators = []
    return StringField(required=True, validate=validators)


def opt_str():
    validators = []
    return StringField(allow_none=True, validate=validators, missing=None)


def req_py_ident():
    validators = [
        validate.Regexp('^[a-zA-Z_][a-zA-Z0-9_]*$',
                        error=u'Może zawierać wyłącznie litery (bez "polskich"), cyfry i znak "_"'),
    ]
    return StringField(required=True, validate=validators)


def opt_py_ident():
    validators = [
        validate.Regexp('^[a-zA-Z_][a-zA-Z0-9_]*$',
                        error=u'Może zawierać wyłącznie litery (bez "polskich"), cyfry i znak "_"'),
    ]
    return StringField(allow_none=True, validate=validators, missing=None)


uuid_regex = {
    'uuid4': '[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\Z',
    'uuid4_hex': '[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z',
}


def req_uuid(regex=uuid_regex['uuid4']):
    validators = [
        validate.Regexp(regex),
    ]
    return StringField(required=True, validate=validators)


def req_slownik(slownik):
    validators = [
        validate.OneOf(slownik.LST_WSZYSTKIE_WARTOSCI),
    ]
    if slownik.LST_WSZYSTKIE_WARTOSCI and isinstance(slownik.LST_WSZYSTKIE_WARTOSCI[0], str):
        return StringField(required=True, validate=validators)
    elif slownik.LST_WSZYSTKIE_WARTOSCI and isinstance(slownik.LST_WSZYSTKIE_WARTOSCI[0], int):
        return ma.Integer(required=True, validate=validators)
    else:
        return StringField(required=True, validate=validators)


def opt_slownik(slownik):
    validators = [
        validate.OneOf(slownik.LST_WSZYSTKIE_WARTOSCI),
    ]
    if slownik.LST_WSZYSTKIE_WARTOSCI and isinstance(slownik.LST_WSZYSTKIE_WARTOSCI[0], str):
        return StringField(allow_none=True, validate=validators, missing={})
    elif slownik.LST_WSZYSTKIE_WARTOSCI and isinstance(slownik.LST_WSZYSTKIE_WARTOSCI[0], int):
        return ma.Integer(allow_none=True, validate=validators, missing={})
    else:
        return StringField(allow_none=True, validate=validators, missing={})


def opt_uuid(regex=uuid_regex['uuid4']):
    validators = [
        validate.Regexp(regex),
    ]
    return StringField(allow_none=True, validate=validators, missing=None)


class FileField(ma.Schema):
    nazwa = req_str()
    mime = req_str()
    rozmiar = req_int(ge=0)
    kodowanie = req_str()
    dane = req_str()


class FileInStorageField(ma.Schema):
    id_pliku = req_ident()
    typ = req_str()


def req_plik():
    return ma.Nested(FileField(), many=False, required=True)


def opt_plik():
    return ma.Nested(FileField(), many=False, allow_none=True, missing=None)


def req_plik_w_magazynie():
    return ma.Nested(FileInStorageField(), many=False, required=True)


def opt_plik_w_magazynie():
    return ma.Nested(FileInStorageField(), many=False, allow_none=True, missing=None)


def schema_list(schema, min_entries=0, required=False):
    validators = []
    if min_entries > 0:
        validators.append(validate.Length(min=min_entries))
    return ma.Nested(schema, many=True, required=required, validate=validators, missing=lambda: [])


def schema(schema):
    return ma.Nested(schema)


class PyField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value

    def _deserialize(self, value, attr, data):
        try:
            compile(value, '<string>', 'exec')
            return value
        except Exception as e:
            log.info('blad', exc_info=True)
            raise ValidationError(u'Podany kod jest niepoprawny: %s' % e)


def req_py_kod(req_fun=[]):
    return PyField(required=True, validate=[])


class StringFieldLiteral(fields.String):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, basestring):
            self.fail('invalid')
        if value is None and getattr(self, 'allow_none', False) is not True:
            self.fail('required')
        return value


def req_str_literal():
    validators = []
    return StringFieldLiteral(required=True, validate=validators)


def opt_str_literal():
    validators = []
    return StringFieldLiteral(allow_none=True, validate=validators, missing=None)


def _validate_pesel(pesel=None):
    if not re.match('[0-9]{11}$', pesel):
        raise ValidationError('PESEL powinien zawierać 11 znaków.')
    else:
        wagi = [9, 7, 3, 1, 9, 7, 3, 1, 9, 7]
        suma = sum(int(pesel[i]) * x for i, x in enumerate(wagi))
        if suma % 10 != int(pesel[-1]):
            raise ValidationError(u'Niepoprawny format PESEL, błędna cyfra kontrolna.')
    return True


def opt_pesel():
    validators = [
        _validate_pesel,
    ]
    return StringField(allow_none=True, validate=validators, missing=None)


def req_pesel():
    validators = [
        _validate_pesel,
    ]
    return StringField(required=True, validate=validators)


def _validate_nip(nip=None):
    if not re.match('[0-9]{10}$', nip):
        raise ValidationError(u'NIP powinien zawierać 10 znaków.')
    else:
        wagi = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        suma = sum(int(nip[i]) * x for i, x in enumerate(wagi))
        cyfra_kontrolna = suma % 11
        if not (cyfra_kontrolna != 10 and cyfra_kontrolna == int(nip[-1])):
            raise ValidationError(u'Niepoprawny format NIP, błędna cyfra kontrolna.')
    return True


def opt_nip():
    validators = [
        _validate_nip,
    ]
    return StringField(allow_none=True, validate=validators, missing=None)


def req_nip():
    validators = [
        _validate_nip,
    ]
    return StringField(required=True, validate=validators)


class DateRangeField(ma.Schema):
    def __init__(self, *args, **kwargs):
        self.date_to_required = kwargs.get('date_to_required')
        self.date_from_required = kwargs.get('date_from_required')
        del(kwargs['date_to_required'])
        del(kwargs['date_from_required'])
        super(DateRangeField, self).__init__(*args, **kwargs)

    date_from = opt_data()
    date_to = opt_data()

    @validates_schema
    def validate(self, data):
        if self.date_to_required and data.get('date_to') is None:
            raise ValidationError(u'Max. data jest wymagana')
        if self.date_from_required and data.get('date_from') is None:
            raise ValidationError(u'Min. data jest wymagana')


def date_range(date_from_required=False, date_to_required=False, required=False):
    return ma.Nested(
        DateRangeField(date_from_required=date_from_required, date_to_required=date_to_required),
        required=required,
        missing=None,
    )
