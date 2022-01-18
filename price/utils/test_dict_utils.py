from .dict_utils import (
    get_sorted_list_from_dict,
)

import logging
log = logging.getLogger(__name__)


def test_get_sorted_list_from_dict():
    data = {
        'key': 'value',
        'zkey': 'value',
    }
    expected_result = ['key', 'zkey']
    result = get_sorted_list_from_dict(data, reverse=True)
    assert result == expected_result
