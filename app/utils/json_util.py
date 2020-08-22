
# from .exceptions import EWindar
import json
import datetime
import dateutil
import decimal
from flask_restful import fields as _fields

import logging
log = logging.getLogger(__name__)


class DateField(_fields.Raw):
    def format(self, value):
        if value is None:
            return {'__tp': 'date', 'value': None}
        try:
            return {'__tp': 'date', 'value': value.isoformat()}
        except Exception as ae:
            raise _fields.MarshallingException(ae)


class DateTimeField(_fields.Raw):
    def format(self, value):
        if value is None:
            return {'__tp': 'datetime', 'value': None}
        try:
            return {'__tp': 'datetime', 'value': value.isoformat()}
        except Exception as ae:
            raise _fields.MarshallingException(ae)


class TimeField(_fields.Raw):
    def format(self, value):
        if value is None:
            return {'__tp': 'time', 'value': None}
        try:
            return {'__tp': 'time', 'value': value.isoformat()}
        except Exception as ae:
            raise _fields.MarshallingException(ae)


class FloatField(_fields.Raw):
    """Flask-RESTful will transform float value to a string before return it.
    This is not useful in most situation, so we change it to return float value directly"""

    def format(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except ValueError as ve:
            raise _fields.MarshallingException(ve)


class IntegerField(_fields.Integer):
    u"""Standardowe pole Integer zwraca 0 dla wartości None"""
    def __init__(self, default=None, **kwargs):
        super(IntegerField, self).__init__(default=default, **kwargs)


class BooleanField(_fields.Raw):
    u"""Standardowe pole Boolean zwraca False dla wartości None"""
    def format(self, value):
        if value is None:
            return None
        return bool(value)


class DecimalField(_fields.Raw):
    def format(self, value):
        if value is None:
            return {'__tp': 'decimal', 'value': None}
        try:
            ret = str(value)
            if '.' in ret:
                ret = ret.rstrip('0').rstrip('.')
            return {'__tp': 'decimal', 'value': ret}
        except Exception as ae:
            raise _fields.MarshallingException(ae)


StringField = _fields.String


class JSONEncodedDictField(_fields.Raw):
    def format(self, value):
        return recursive_default_handler(value)


_load_json_type_conversions = {
    'decimal': lambda dct: decimal.Decimal(dct['value']),
    'datetime': lambda dct: dateutil.parser.parse(dct['value']),
    'date': lambda dct: dateutil.parser.parse(dct['value']).date(),
}


def _default_read_handler(x):
    x_type = x.get('__tp')
    if x_type:
        conv = _load_json_type_conversions.get(x_type)
        if conv:
            return conv(x)
    return x


_json_type_conversions = {
    decimal.Decimal: DecimalField().format,
    datetime.datetime: DateTimeField().format,
    datetime.date: DateField().format,
}


def _default_write_handler(x):
    conv = _json_type_conversions.get(x.__class__)
    if conv:
        return conv(x)
    return x


def recursive_default_handler(value):
    if isinstance(value, list):
        return [recursive_default_handler(v) for v in value]
    elif isinstance(value, dict):
        if '__tp' in value:
            return _default_read_handler(value)
        return dict(
            (k, recursive_default_handler(v))
            for k, v in value.iteritems()
        )
    elif isinstance(value, (datetime.date, datetime.datetime, decimal.Decimal)):
        return _default_write_handler(value)
    elif isinstance(value, tuple) and hasattr(value, '_asdict'):
        # to najprawdopodobniej namedtuple - zapisujemy jakby to byl slownik
        return recursive_default_handler(value._asdict())
    return value


def dumps_with_objects(wartosc, indent=None):
    return json.dumps(wartosc, default=_default_write_handler, indent=indent)


def loads_with_objects(wartosc):
    def _default_handler(x):
        x_type = x.get('__tp')
        if x_type:
            conv = _load_json_type_conversions.get(x_type)
            if conv:
                return conv(x)
            else:
                #raise EWindar(u'Pole zawiera nieobsługiwany typ, __tp=%s' % x.get('__tp'))
                raise Exception(u'Pole zawiera nieobsługiwany typ, __tp=%s' % x.get('__tp'))
        else:
            return x
    return json.loads(wartosc, object_hook=_default_handler)
