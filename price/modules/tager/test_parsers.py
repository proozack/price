from price.modules.tager.parsers import (
    search_by_key,
    search_like_key,
    neighborhood_analysis
)

import logging
log = logging.getLogger(__name__)


def test_search_by_key():
    colors = [
        (1, 'czerwonym'),
        (2, 'czarnym'),
        (3, 'niebieski')
    ]
    input_val = [
        ('w czerwonym słońcu', [(1, 'czerwonym', 2), ]),
        ('w czerwonym słońcu, czerwonym świecie', [(1, 'czerwonym', 2), ]),
        ('w czerwonym słońcu w czarnym lesie', [(1, 'czerwonym', 2), (2, 'czarnym', 21), ]),
        ('w sweicie bez kolorów', []),
        ('niebieska sukienka, z czerwonymi rękawami i czanymi kokardami', [(3, 'niebieski'), (1, 'czerwonym', 2), (2, 'czarnym', 21), ]) # noqa E501

    ]
    for case, expected in input_val:
        assert search_by_key(case, colors) == expected


def test_search_like_key():
    colors = [
        (1, 'czerwony'),
        (2, 'czarny'),
        (3, 'niebieski')
    ]
    input_val = [
        ('w czerwonym słońcu', [(1, 'czerwony'), ]),
        ('w czerwonym słońcu, czerwonym świecie', [(1, 'czerwony'), ]),
        ('w czerwonym słońcu w czarnym lesie', [(1, 'czerwony'), (2, 'czarny'), ]),
        ('w sweicie bez kolorów', []),
        ('niebieska sukienka, z czerwonymi rękawami i czarną kokardą', [(1, 'czerwony'), (2, 'czarny'), (3, 'niebieski')]), # noqa E501
        ('śmieci na końcu', [])
    ]
    for case, expected in input_val:
        # log.error('{} == {}'.format(search_like_key(case, colors), expected))
        assert search_like_key(case, colors) == expected


def test_neighborhood_analysis():
    brands = [
        (1, 'lupoline'),
        (2, 'softline collection'),
    ]

    input_val = [
        ('lupo line body koronkowe', [(1, 'lupoline')]),
        ('softline collection body', []),
    ]
    for case, expected in input_val:
        assert neighborhood_analysis(case, brands) == expected
