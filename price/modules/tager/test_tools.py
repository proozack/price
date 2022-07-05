from .tools import (
    clear_title,
    split_title,
    generate_similar_tag,
    clean_data,
    search_str,
    spli_tekst,
    join_tabs
)

import logging
log = logging.getLogger(__name__)


def test_clear_title():
    data = 'Example.title#'
    expected_result = 'example title'
    result = clear_title(data)
    assert result == expected_result


def test_split_title():
    data = 'Example a title'
    expected_result = 'Example title'
    result = split_title(data)
    assert result == expected_result


def test_generate_similar_tag():
    data = 'test'
    expected_result = {'names': [
            'test',
            'test',
            '-test-',
            '-test',
            'test-',
            'test',
            '_test_',
            '_test',
            'test_'],
         'tag': 'test',
    }
    result = generate_similar_tag(data)
    assert result == expected_result


def test_clear_data():
    lst_input = [
        ('Luna/BO body czarne S-XXL', 'luna bo body czarne s xxl'),
        ('Julimex Flexi-One Body', 'julimex flexi one body'),
        ('Koszulka Mey Emotion Elegance Top 55360/55370', 'koszulka mey emotion elegance top 55360 55370'),
        ('Moon/Bo Body Srebrny', 'moon bo body srebrny')
    ]

    for case, expected in lst_input:
        assert clean_data(case) == expected


def test_search_brand():
    lst_brand = [
        (1, 'anais'),
        (2, 'livia corsetti'),
        (3, 'babel'),
        (4, 'gaia'),
        (5, 'gorsnia'),
        (6, 'julimex'),
        (7, 'lupoline'),
        (8, 'ava')
    ]
    lst_input = [
        ('anais body sallena', [(1, 'anais'), ]),
        ('anais body sallena gaia', [(1, 'anais'), (4, 'gaia')]),
        ('babel liliava 28', [(3, 'babel'), (8, 'ava')]),
        ('anais body anais sallena', [(1, 'anais'), ]),
        ('gorteks luna bo body sexy, czarny', []),
    ]
    for case, expected in lst_input:
        assert search_str(case, lst_brand) == expected


def test_spli_tekst():
    lst_input = [
        ('anais body sallena', ['anais', 'body', 'sallena']),
        (' anais body sallena', ['anais', 'body', 'sallena']),
        ('anais  body sallena', ['anais', 'body', 'sallena']),
        ('anais body sallena ', ['anais', 'body', 'sallena']),
    ]
    for case, expected in lst_input:
        assert spli_tekst(case) == expected


def test_join_tabs():
    lst_input = [
        (['anais', 'body', 'sallena'], 'anais body sallena'),
    ]
    for case, expected in lst_input:
        assert join_tabs(case) == expected
