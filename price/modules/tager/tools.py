import logging
log = logging.getLogger(__name__)


bad_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~'] # noqa E501


def clear_title(title):
    for c in bad_characters:
        title = title.replace(c, '')
    return title.lower()


def split_title(title):
    list_element = []
    for element in title.split(' '):
        if element != ' ' and len(element) > 1:
            list_element.append(element)
    return ' '.join(list_element)
