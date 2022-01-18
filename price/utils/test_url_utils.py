import pytest
from .url_utils import UrlUtils


import logging
log = logging.getLogger(__name__)

pytest.global_var = {}


def test_url_utils():
    link = 'http://test.com.pl/?attr1=1&atr2=str'
    link1 = 'https://test.com.pl/?attr1=1&atr2=str'
    link2 = 'htt://test.com/'
    link3 = 'http//test.com/test.jpg'
    link4 = 'http://test.com.pl/strona.htm'
    u = UrlUtils()
    assert u.get_protocol(link) == 'http'
    assert u.get_protocol(link1) == 'https'
    assert u.get_domain(link) == 'test.com.pl'
    assert u.is_correct_url(link) is True
    assert u.is_correct_url(link2) is False
    assert u.check_protocol(link) is True
    assert u.check_protocol(link2) is False
    assert u.get_url_string(link) == '?attr1=1&atr2=str'
    assert u.get_attr_from_url(link) == 'attr1=1&atr2=str'
    r = u.get_dicts_from_args(link)
    assert len(r) == 2
    assert r.get('attr1') == '1'
    assert r.get('atr2') == 'str'
    assert u.check_if_domain_exists(link) is True
    assert u.is_image(link3) is True
    assert u.is_image(link) is False
    assert u.is_page('') is False
    assert u.is_page(link4) is True
    assert u.is_page(link2) is False


def test_generate_link():
    domain = 'http://test.com.pl/'
    link = '?attr1=1&atr2=str'
    link1 = 'http://test.com.pl/?attr1=1&atr2=str'
    link2 = '/?attr1=1&atr2=str'
    expected_result = 'http://test.com.pl/?attr1=1&atr2=str'
    u = UrlUtils(domain)
    result = u.generate_link(link)
    result1 = u.generate_link(link1)
    result2 = u.generate_link(link2)
    assert result is False
    assert result1 == expected_result
    assert result2 == expected_result
