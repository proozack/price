from typing import NoReturn
from .tools import (
    # split_text,
    # search_str,
    spli_tekst,
    join_tabs,
    clean_data
)
from .parsers import processing_tools


import logging
log = logging.getLogger(__name__)


class Definitions():
    def __init__(self, brands: list = [], categories: list = [], colors: list = [], sizes: list = []) -> NoReturn: # noqa E501
        self.__brands = brands
        self.__categories = categories
        self.__colors = colors
        self.__sizes = sizes

    def load_brands(self, brands: list) -> NoReturn:
        self.__brands = brands

    @property
    def brands(self) -> list:
        return self.__brands

    def load_categories(self, categories: list) -> NoReturn:
        self.__categories = categories

    @property
    def categories(self) -> list:
        return self.__categories

    def load_colors(self, colors: list) -> NoReturn:
        self.__colors = colors

    @property
    def colors(self) -> list:
        return self.__colors

    def load_sizes(self, sizes: list) -> NoReturn:
        self.__sizes = sizes

    @property
    def sizes(self) -> list:
        return self.__sizes


class AnalyzedText():
    def __init__(self, text):
        self.__load_processing_tools(processing_tools)
        self.__org_text = text
        self.__clean_data = clean_data(self.__org_text)
        self.__tags = spli_tekst(self.__clean_data)
        self.__text = join_tabs(self.__tags)
        self.__case_dct = {
            'org_text': self.__org_text,
            'text': self.__text,
            'tags': self.__tags,
        }

    def __repr__(self) -> str:
        return '<#AnalyzedText: "{}"'.format(self.__text[0:50])

    @property
    def org_text(self) -> str:
        return self.__org_text

    @property
    def text(self) -> str:
        return self.__text

    @property
    def tags(self) -> list:
        return self.__tags

    @property
    def brand(self, method='search_like_key') -> list:
        result = self.__processing_tools.get(method)(
            self.__case_dct.get('text'),
            self.__definitions.brands,
        )
        if not result:
            result = self.__processing_tools.get('neighborhood_analysis')(
                self.__case_dct.get('text'),
                self.__definitions.brands,
            )
        return result

    @property
    def category(self, method='search_like_key') -> list:
        return self.__processing_tools.get(method)(
            self.__case_dct.get('text'),
            self.__definitions.categories,
        )

    @property
    def color(self, method='search_like_key') -> list:  # change to teh list of colors
        return self.__processing_tools.get(method)(
            self.__case_dct.get('text'),
            self.__definitions.colors,
        )

    @property
    def size(self) -> list:
        return []

    def __load_processing_tools(self, processing_tools: dict) -> NoReturn:
        self.__processing_tools = processing_tools

    def load_definitions(self, definitions: Definitions):
        self.__definitions = definitions

    # both of the following functions will be to replace, to universal tools.
    def get_brand(self) -> list:
        pass

    def get_categories(self) -> list:
        pass
