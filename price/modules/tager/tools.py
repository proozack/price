# from typing import Tuple

import logging
log = logging.getLogger(__name__)


bad_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~'] # noqa E501


def clear_title(title):
    for c in bad_characters:
        title = title.replace(c, '')
    return title.lower().strip()


def split_title(title):
    list_element = []
    for element in title.split(' '):
        if element != ' ' and len(element) > 1:
            list_element.append(element)
    return ' '.join(list_element)


def split_text(text):
    return text.split(' ')


def generate_similar_tag(value):
    value = value.strip().lower()
    names = []
    names.append(value)
    for char in ['-', '_']:
        names.append(value.replace(' ', char))
        names.append('{}{}{}'.format(char, value.replace(' ', char), char))
        names.append('{}{}'.format(char, value.replace(' ', char)))
        names.append('{}{}'.format(value.replace(' ', char), char))
    return {
        'tag': value,
        'names': names,
    }


def clean_data(data: str) -> str:
    for char in bad_characters:
        data = data.replace(char, ' ')
    return data.lower()


def spli_tekst(data: str) -> list:
    lst_tag = []
    tmp_tag = data.split(' ')
    for tag in tmp_tag:
        if tag != ' ' and tag != '':
            lst_tag.append(tag)
    return lst_tag


def search_str(data: str, key_lst: list) -> list:
    found_keys = []
    for key_id, key_name in key_lst:
        if key_name in data:
            found_keys.append((key_id, key_name))
    return found_keys


def join_tabs(keys_list: list) -> list:
    return ' '.join(keys_list)
