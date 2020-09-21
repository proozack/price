from collections import namedtuple

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
        'image'
    ]
)

MenuLink = namedtuple(
    'MenuLink',
    [
        'name',
        'representation',
        'parent']
    )
