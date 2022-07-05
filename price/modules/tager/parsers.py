import morfeusz2
import logging
log = logging.getLogger(__name__)


def search_by_key(text: str, entities: list) -> list:
    found_keys = []
    for entiti in entities:
        position = text.find(entiti[1])
        if position >= 0:
            found_keys.append((entiti[0], entiti[1], position))
    return found_keys


def search_like_key(text: str, entities: list) -> list:
    """
    text should be clear from bank char
    """
    morf = morfeusz2.Morfeusz()
    found_keys = []
    for entiti in entities:
        for word in text.split(' '):
            result = morf.analyse(word)
            tmp_tab = result[0][2][1].split(':')
            if len(tmp_tab):
                if tmp_tab[0] == entiti[1]:
                    if entiti not in found_keys:
                        found_keys.append(entiti)
    return found_keys


def neighborhood_analysis(text: str, entities: list) -> list:
    found_keys = []
    last_key = None
    for entiti in entities:
        for word in text.split(' '):
            new_str = "{}{}".format(last_key, word)
            if new_str == entiti[1]:
                found_keys.append(
                    (
                        entiti[0],
                        entiti[1],
                    )
                )
            last_key = word
    return found_keys


processing_tools = {
    'search_by_key': search_by_key,
    'search_like_key': search_like_key,
    'neighborhood_analysis': neighborhood_analysis,
}
