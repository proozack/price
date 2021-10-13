u"""Narzędzia do pracy z marshal() z flask-restful

Na podstawie
https://github.com/anjianshi/flask-restful-extend/blob/master/flask_restful_extend/marshal.py
"""

from sqlalchemy.sql.sqltypes import Numeric
from flask_restful import fields as _fields
from .json_util import DateField, DateTimeField, FloatField, IntegerField, TimeField
from .json_util import BooleanField, DecimalField, StringField, JSONEncodedDictField
import datetime
import decimal

import logging
log = logging.getLogger(__name__)


_marshal_type_map = {
    # python_type: flask-restful field
    'str': StringField,
    'unicode': StringField,
    'int': IntegerField,
    'float': FloatField,
    'bool': BooleanField,
    'datetime': DateTimeField,
    'date': DateField,
    'time': TimeField,
    'Decimal': DecimalField,
    'dict': JSONEncodedDictField,
    'timedelta': IntegerField,
}


class MetaEmulacjaObiektuSqla(type):
    def __init__(cls, name, bases, dct):
        column_descriptions = []
        for meta in dct['bazowe_tabele_sqla']:
            t = meta['tabela']
            pomin = meta.get('pomin')
            for col in t.__table__.columns:
                if not (pomin and col in pomin):
                    column_descriptions.append({
                        'name': col.name,
                        'type': col.type,
                    })
        cls.column_descriptions = column_descriptions


class EmulacjaObiektuSqla(object):
    u"""Klasa bazowa zapewniająca kompatybilność z obiektami typu SQLA Query
    na potrzeby mechanizmu marshal.
    """

    __metaclass__ = MetaEmulacjaObiektuSqla

    u"""Atrybut wymagany do zdefiniowania w klasie potomnej - lista słowników
    gdzie pole `tabela` musi zawierać odwołanie do klasy tabeli sqlalchemy
    a opcjonalne pole `pomin` to lista kolumn z tej tabeli, które nie będą
    przepisywane do emulowanego obiektu.
    """
    bazowe_tabele_sqla = []

    @classmethod
    def mk_z_obiektow_sqla(cls, *obiekty):
        u"""Utworzenie nowego obiektu i jednocześnie zainicjowanie
        go wartościami z podanych obiektów SQLA. Obiekty te muszą należeć
        do klas wskazanych w atrybucie `bazowe_tabele_sqla`."""
        self = cls()
        self.pobierz_dane_z_obiektow_sqla(*obiekty)
        return self

    def pobierz_dane_z_obiektow_sqla(self, *obiekty):
        u"""Metoda pozwalająca na pobranie wartości ze wskazanych obiektów.
        Obiekty te muszą należeć do klas wskazanych w atrybucie
        `bazowe_tabele_sqla`."""
        for ob in obiekty:
            for meta in self.bazowe_tabele_sqla:
                t = meta['tabela']
                if isinstance(ob, t):
                    pomin = meta.get('pomin')
                    for col in t.__table__.columns:
                        if not (pomin and col in pomin):
                            setattr(self, col.name, getattr(ob, col.name))


def _get_columns_from_query(query, mapa_podobiektow_sqla):
    def simple_name(info, col):
        return col.name

    def compound_name(info, col):
        return '%s.%s' % (info['name'], col.name)
    ret = []
    for info in query.column_descriptions:
        if hasattr(info['type'], '__table__'):
            if mapa_podobiektow_sqla:
                podobiekt = mapa_podobiektow_sqla.get(info['type'].__table__)
            else:
                podobiekt = None
            # kwerendy typu query(KlasaZmapowana) w polu expr mają obiekt Mapper
            # a ich wartości trafiają do głównego obiektu zwracanego przez sqla
            # natomiast kwerendy bardziej złożone np query(KlasaZmapowana1, KlasaZmapowana2)
            # w polu expr mają klasę zmapowaną, tą samą co w polu type, a ich wartości
            # trafiają do podobiektu o nazwie wskazywanej polem name
            if info['type'] is info['expr']:
                mk_name = compound_name
            else:
                mk_name = simple_name
            for col in info['type'].__table__.columns:
                ret.append((podobiekt, col.name, mk_name(info, col), col.type))
        else:
            if mapa_podobiektow_sqla:
                expr = info['expr']
                if expr.expression in mapa_podobiektow_sqla:
                    podobiekt = mapa_podobiektow_sqla[expr.expression]
                elif hasattr(expr, 'element') and expr.element in mapa_podobiektow_sqla:
                    podobiekt = mapa_podobiektow_sqla[expr.element]
                else:
                    podobiekt = None
            else:
                podobiekt = None
            ret.append((podobiekt, info['name'], info['name'], info['type']))
    return ret


def marshal_fields_for_sqla_model(column_source, mapa_podobiektow_sqla=None):
    u"""Tworzy słownik pól zgodnych z mechanizmem marshal() z flask-restful.

    Parametr `column_source` może zawierać zmapowaną klasę albo obiekt
    kwerendy sqlalchemy. Generowane są pola o nazwach takich jak nazwy kolumn
    i typach określonych na podstawie typu danych w tych kolumnach (na bazie
    mapowania z `_marshal_type_map`).

    Jeśli `column_source` to kwerenda to parametr `mapa_podobiektow_sqla` może
    zawierać słownik mapujący obiekt tabeli lub zmapowanej klasy sqlalchemy na
    string. W takim przypadku jeśli kwerenda zawiera klauzule pobierające
    całe obiekty a nie konkretne kolumny to wartości z tych obiektów trafią do
    zagnieżdżonego słownika o nazwie wskazanej w `mapa_podobiektow_sqla`. Jeśli
    jakiegoś obiektu nie ma w mapie to jego kolumny trafią do głównego słownik
    wynikowego.

    Na przykład dla kwerendy

        db.session.query(
            KSI_V_Dluznicy.dluznik_nazwa,
            KSI_V_Dluznicy.dluznik_imie,
            Ugoda,
            KSI_V_Adresy,
            KSI_V_Telefony,
        )

    oraz dla mapy

        mapa_podobiektow_sqla = {
            Ugoda: 'ugoda',
            KSI_V_Adresy: 'adres',
        }

    dostaniemy słownik:

        {
            'ugoda': { ... pola z tabeli Ugoda ... },
            'adres': { ... pola z tabeli KSI_V_Adresy .. },
            ... pola z tabeli KSI_V_Telefony oraz imię i nazwisko dłużnika ...
        }
    """
    if mapa_podobiektow_sqla:
        # upewniam sie ze kluczami w mapie sa tabele lub kolumny a nie zmapowane klasy lub wyrazenia
        popr_mapa = {}
        for k, v in mapa_podobiektow_sqla.iteritems():
            if hasattr(k, '__table__'):
                popr_mapa[k.__table__] = v
            elif hasattr(k, 'expression'):
                popr_mapa[k.expression] = v
            else:
                popr_mapa[k] = v
        mapa_podobiektow_sqla = popr_mapa

    field_definition = {}
    if hasattr(column_source, '__table__'):
        column_source = [(None, col.name, col.name, col.type) for col in column_source.__table__.columns]
    else:
        column_source = _get_columns_from_query(column_source, mapa_podobiektow_sqla)
    for podobiekt, col_name, src_attr, col_type in column_source:
        field_para = {}
        if col_name != src_attr:
            field_para['attribute'] = src_attr

        if not podobiekt:
            dest_field_definition = field_definition
        elif podobiekt in field_definition:
            dest_field_definition = field_definition[podobiekt]
        else:
            dest_field_definition = {}
            field_definition[podobiekt] = dest_field_definition

        # sprawdzam decimale po nazwie zmapowanego typu oraz po typie kolumny
        # poniewaz mechanizm reflection moze przypisac do python_type typ float zamiast Decimal
        # nie pomaga nawet parametr coerce_to_decimal podany do engine...
        is_decimal = col_type.python_type.__name__ == 'Decimal' or isinstance(col_type, Numeric)
        if is_decimal and col_type.scale == 0:
            dest_field_definition[col_name] = _marshal_type_map['int'](**field_para)
        elif is_decimal:
            dest_field_definition[col_name] = _marshal_type_map['Decimal'](**field_para)
        else:
            dest_field_definition[col_name] = _marshal_type_map[col_type.python_type.__name__](**field_para)

    return field_definition


def marshal_fields_for_sqla_model_list(model, excludes=None, only=None, extends=None):
    return _fields.List(_fields.Nested(marshal_fields_for_sqla_model(model, excludes, only, extends)))


def lista_obiektow_do_selitems(iter_ob, pole_wartosci, pole_nazwy='nazwa'):
    u'''
    Funkcja zwraca liste słowników dla selItems do wykorzystania na gui.
    Klucze słowników to 'nazwa' i 'id'
    :param lst_ob: lista obiektów do iteracji. Musi posiadac atrybuty podane w reszcie argumentów,
    :type lst_ob: dowolny obiekt iterowalny,
    :param pole_wartosci: pole do pobierania wartości dla selItems,
    :type pole_wartosci: class `str`
    :param pole_nazwy: pole do pobierania nazwy dla selItems,
    :type pole_nazwy: class `str`
    :rtype: lista słowników
    '''
    return [{'nazwa': getattr(ob, pole_nazwy), 'id': getattr(ob, pole_wartosci)} for ob in iter_ob]


_decimal_field = DecimalField()
_datetime_field = DateTimeField()
_date_field = DateField()


def marshal_sqla_result(iter_src_data, column_type_override=None):
    u'''
    Zamienia SQLAlchemy ResultProxy na dict konwertując wartości zgodnie ze słownikiem `type_conversions`.
    :param `iter` iter_src_data: wynik zapytania sql
    :param `dict` column_type_override: słowników funkcji indywidualnej konwersji dla nazwy kolumny
    :rtype: `list` : `dict`
    '''
    type_conversions = {
        decimal.Decimal: _decimal_field.format,
        datetime.datetime: _datetime_field.format,
        datetime.date: _date_field.format,
        'decimal': _decimal_field.format,
        'datetime': _datetime_field.format,
        'date': _date_field.format,
    }
    column_type_override = column_type_override or {}

    def _mk_dct_from_item(item):
        ret = {}
        for name, value in item.items():
            tp_conv = type_conversions.get(column_type_override.get(name, type(value)))
            if tp_conv is not None:
                ret[name] = tp_conv(value)
            else:
                ret[name] = value
        return ret
    return [
        _mk_dct_from_item(item)
        for item in iter_src_data
    ]
