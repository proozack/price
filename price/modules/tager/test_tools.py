from .tools import (
    clear_title,
    split_title,
    generate_similar_tag
)

import logging
log = logging.getLogger(__name__)


def test_clear_title():
    data = 'Example.title#'
    expected_result = 'exampletitle'
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
