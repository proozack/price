from collections import namedtuple


import logging
log = logging.getLogger(__name__)

Dimension = namedtuple(
    'Dimension',
    [
        'width',
        'height',
        'channel',
    ]
)

Ofert = namedtuple(
    'Ofert',
    [
        'title',
        'price',
        'currency',
        'url',
        'image',
        'manufacturer'
    ]
)

MenuLink = namedtuple(
    'MenuLink',
    [
        'name',
        'representation',
        'parent']
    )


class LocalType():
    def set_attr_from_kwargs(self, **kwargs):
        self._fields = []
        for field in kwargs:
            setattr(self, field, kwargs.get(field))
            self._fields.append(field)

    def add_field(self, field, value):
        if not hasattr(self, field):
            setattr(self, field, value)
            self._fields.append(field)
        else:
            log.warning('Object %r  already has a field %r', self, field)

    def get_dict(self):
        return {
            field: getattr(self, field)
            for field in self._fields
        }

    def __repr__(self):
        return '{}'.format(self.__class__)


class TempProduct(LocalType):
    def __init__(self, **kwargs):
        self.set_attr_from_kwargs(**kwargs)
