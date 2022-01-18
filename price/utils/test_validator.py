import pytest
from .validator import (
    ValidationError,
    img_extension_validation,
    url_protocol_validation,
    is_www_img,
    is_web_page,
)


def test_img_extension_validation():
    link1 = 'http://test.com.pl/test.jpg'
    link2 = 'https://test.com.pl/test.gif'
    link3 = 'http://test.com.pl/test1.html'

    assert img_extension_validation(link1) == link1
    assert img_extension_validation(link2) == link2
    with pytest.raises(ValidationError, match=r".*image*"):
        img_extension_validation(link3) is False


def test_url_protocol_validation():
    link1 = 'http://test.com.pl'
    link2 = 'https://test.com.pl'
    link3 = 'smb://test.com.pl'
    url_protocol_validation(link1) is link1
    url_protocol_validation(link2) is link2
    with pytest.raises(ValidationError, match=r".*correct url*"):
        url_protocol_validation(link3) is False


def test_is_www_img():
    link1 = 'http://test.com.pl/test.jpg'
    link2 = 'http://test.com.pl/test.html'
    link3 = 'smb://test.com.pl/test.jpg'
    is_www_img(link1) is link1
    with pytest.raises(ValidationError, match=r".*image*"):
        is_www_img(link2) is False

    with pytest.raises(ValidationError, match=r".*correct url*"):
        is_www_img(link3) is False


def test_is_web_page():
    link1 = 'http://test.com.pl/test.html'
    link2 = 'https://test.com.pl/test.html'
    link3 = 'smb://test.com.pl'
    is_web_page(link1) is link1
    is_web_page(link2) is link2
    with pytest.raises(ValidationError, match=r".*correct url*"):
        is_web_page(link3) is False
