from bs4 import BeautifulSoup
# import pprint

from .parser import AbstractParser
from app.utils.download_utils import SmallResponseObject
from . import parsers_collection as pcoll
from .collection_of_catalogs_parsers import catalogs_parser_wrapper
# div_catalogs_parser, article_catalogs_parser
from .data_digger import (DomodiPl, IntimitiPl, NoshamePl, SwiatbieliznyPl, IntymnaPl, OhsoPl, ByannPl, KontriPl, SensualePl, ELadyPl, UlubionabieliznaPl, MagicznabieliznaPl) # noqa F401

import logging
log = logging.getLogger(__name__)


class GaleryParser(AbstractParser):

    def __init__(self):
        self._soup = None
        self._response_object = None
        self.m = None

    def set_response(self, value: SmallResponseObject):
        self._response_object = value
        self._soup = BeautifulSoup(value.get_contents(), features="html.parser")
        domain_parser_class = self._response_object.domain.title().replace('.', '').replace('-', '')
        self.m = globals()[domain_parser_class](self._response_object)

    def get_list_links_from_page(self) -> list:
        link_list = [
            link.get("href")
            for link in self._soup.find_all("a")
        ]
        pcoll.domain = self._response_object.domain
        link_list = pcoll.gallery_parser(link_list)
        return link_list

    def get_list_image_from_page(self) -> list:
        image_list = [
            link.get("src")
            for link in self._soup.find_all("img")
        ]
        # log.info(image_list)
        pcoll.domain = self._response_object.domain
        image_list = pcoll.gallery_parser(image_list)
        return image_list

    def get_title(self) -> str:
        pass

    def get_entity(self) -> list:
        self.get_next_page()
        result = []
        manual_assignment_to_div = [
            'allegro.pl'
        ]
        parsers_type = 'div'
        count_article = 0

        manual_assignment_dict = {
            'intymna.pl': 'div_row',
            'swiatbielizny.p': 'div',
            'noshame.pl': 'figure',
            'ohso.pl': 'div_kat_prod',
            'byann.pl': 'div_product',
            'kontri.pl': 'div_item_product',
            'sensuale.pl': 'div_product',
            'e-lady.pl': 'div_product_box',
            'magicznabielizna.pl': 'div_multi_class',
        }

        for wyn in self._soup.find_all('article'):
            count_article += 1

        if count_article > 1 and self._response_object.domain not in manual_assignment_to_div:
            parsers_type = 'article'

        if self._response_object.domain in manual_assignment_dict.keys():
            parsers_type = manual_assignment_dict.get(self._response_object.domain)

        for field in catalogs_parser_wrapper(parsers_type, self._soup):
            wyn = self.m.parse_entity(field)
            result.append(wyn)

        return result

    def get_next_page(self):
        return self.m.get_next(self._soup)