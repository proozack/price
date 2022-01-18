import pytest
from url_utils import UrlUtils


import logging
log = logging.getLogger(__name__)

pytest.global_var = {}


def create_object():
    return UrlUtils()
