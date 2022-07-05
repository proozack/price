import pytest
from price.modules.tager.local_types import (
    AnalyzedText,
    Definitions,
)


@pytest.fixture
def conf_dct():
    definitions = {
        'brands': [
            (1, 'anais'),
            (2, 'eldar'),
            (3, 'lupoline'),
        ],
        'categories': [
            (1, 'body'),
            (2, 'majtki'),
        ],
        'colors': [
            (1, 'czarny'),
            (2, 'biały'),
        ],
        'sizes': [
            (1, 'xxl'),
            (2, 'xl'),
        ],
    }
    return definitions


def test_definitions(conf_dct):
    d = Definitions(conf_dct.get('brands'), conf_dct.get('categories'), conf_dct.get('colors'), conf_dct.get('sizes'))
    d1 = Definitions()

    d1.load_brands(conf_dct.get('brands'))
    d1.load_categories(conf_dct.get('categories'))
    d1.load_colors(conf_dct.get('colors'))
    d1.load_sizes(conf_dct.get('sizes'))

    assert d.brands == conf_dct.get('brands')
    assert d.categories == conf_dct.get('categories')
    assert d.colors == conf_dct.get('colors')
    assert d.sizes == conf_dct.get('sizes')

    assert d1.brands == conf_dct.get('brands')
    assert d1.categories == conf_dct.get('categories')
    assert d1.colors == conf_dct.get('colors')
    assert d1.sizes == conf_dct.get('sizes')


def test_analyzed_text(conf_dct):
    input_lst = [
        ('próbny text dla testów', ('próbny text dla testów', ['próbny', 'text', 'dla', 'testów'], [], [], [])),
        ('śmieci na końcu ', ('śmieci na końcu', ['śmieci', 'na', 'końcu'], [], [], [])),
        ('anais body sallena', ('anais body sallena', ['anais', 'body', 'sallena'], [(1, 'anais')], [(1, 'body')], [])),
        ('anais body z czarnymi majtkami m-7087', ('anais body z czarnymi majtkami m 7087', ['anais', 'body', 'z', 'czarnymi', 'majtkami', 'm', '7087'], [(1, 'anais')], [(1, 'body'), (2, 'majtki')], [(1, 'czarny')])), # noqa E501
        ('lupoline 206 body', ('lupoline 206 body', ['lupoline', '206', 'body'], [(3, 'lupoline')], [(1, 'body')], [])),
        ('lupo line 207 body', ('lupo line 207 body', ['lupo', 'line', '207', 'body'], [(3, 'lupoline')], [(1, 'body')], [])), # noqa E501
    ]
    d = Definitions(
        conf_dct.get('brands'),
        conf_dct.get('categories'),
        conf_dct.get('colors'),
        conf_dct.get('sizes')
    )
    for case, expected in input_lst:
        at = AnalyzedText(case)
        at.load_definitions(d)
        assert at.text == expected[0]
        assert at.tags == expected[1]
        assert at.org_text == case
        assert at.brand == expected[2]
        assert at.category == expected[3]
        assert at.color == expected[4]
