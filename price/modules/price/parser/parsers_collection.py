from typing import Any
from price.utils.url_utils import UrlUtils


import logging
log = logging.getLogger(__name__)

domain = None

uu = UrlUtils()


def is_this_same_domain(value):
    if uu.get_domain(value) == domain:
        return value


def is_not_none(value):
    if value is not None:
        return value


def remove_one_char(value):
    if len(value) > 3:
        return value


def custom_parser(values_list: Any, list_parser: list) -> list:
    for parser_name in list_parser:
        temp = []
        val = None
        for value in values_list:
            val = parser_name(value)
            if val:
                temp.append(val)
        values_list = temp
    return values_list


def gallery_parser(value_list):
    parser_list = [
        is_not_none,
        remove_one_char,
        is_this_same_domain,
    ]
    return custom_parser(value_list, parser_list)
