from typing import Callable, Any
from importlib import import_module
from bs4 import BeautifulSoup
from price.utils.download_utils import standard_request, SmallResponseObject
from price.modules.imp_price.local_types import ProductPage 


import logging
log = logging.getLogger(__name__)


class PageDownloader():
    def __init__(self, url):
        self.url = url
        self.data_model = None

    def download_page(self, url: str = None) -> SmallResponseObject:
        if url is None:
            url = self.url
        sro = standard_request(url)
        return sro

    def parse_page(self, page_body: str, paraser: Callable) -> Any:
        soup = BeautifulSoup(page_body, features="html.parser")
        self.data_model = paraser(soup)

    def get_data(self):
        return self.data_model


def get_parser_by_domain(sro: SmallResponseObject) -> Any:
        domain_parser_class = sro.domain.title().replace('.', '').replace('-', '')
        module = import_module('price.modules.price.parser.data_digger')
        mod = getattr(module, domain_parser_class)
        return mod(sro)
