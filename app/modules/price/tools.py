import requests
from bs4 import BeautifulSoup
from app.modules.price.db_utils import BrandDbUtils, OfertDbUtils
from app.utils.url_utils import UrlUtils

import logging
log = logging.getLogger(__name__)


class ProductTools():
    def __init__(self):
        self.bdbu = BrandDbUtils()
        self.brands_list = self.bdbu.get_all_brand_as_list()

    def search_brand(self, title):
        """
        this cod is wrong shoul by rfactoring
        """
        title_list = title.split(' ')
        for title_element in title_list:
            if title_element in self.brands_list:
                return title_element
        return False

    def remove_brand_from_title(self, title, manufacturer):
        result = self.search_brand(title)
        if not result:
            result = ''
        return (
            title.replace(
                result,
                ''
            ).strip(),
            None if result == '' else result,
            manufacturer
        )


class OfertTools():
    def __init__(self):
        pass

    def parse_title(self, category_id):
        p = ProductTools()
        o = OfertDbUtils()
        for ofert in o.get_all_ofert_by_category(category_id):
            name = ofert[1]
            manufacturer = ofert[4]
            parsed_title = p.remove_brand_from_title(name, manufacturer)
            yield parsed_title


class BrandTools():
    def __init__(self):
        pass

    def enrich_brands_list(self, category_id: int):
        odbu = OfertDbUtils()
        bdbu = BrandDbUtils()
        for brand_name in odbu.get_all_brand_by_category(category_id):
            if not bdbu.is_brand_exists(brand_name):
                log.info('Adding brand %r', brand_name)
                bdbu.add_brand(brand_name)

    def download_brand_from_page(self):
        """
        This method should be move to another place
        """
        path = 'http://egusti.pl/marki'
        r = requests.get(path)
        url = UrlUtils(path)
        soup = BeautifulSoup(r.text, features="html.parser")
        producer = soup.findAll(attrs={'class': 'manufacturer'})
        bdbu = BrandDbUtils()
        for prod in producer:
            raw_img = prod.findAll('img')
            path_url = raw_img[0].get('src')
            raw_prod = prod.findAll(attrs={'class': 'manufacturer-name'})
            name = raw_prod[0].text
            if not bdbu.is_brand_exists(name):
                logo = '{}://{}{}'.format(url.protocol, url.domain, path_url)
                ins = {'name': raw_prod[0].text, 'logo': logo}
                # log.info('Dict: %r', ins )
                bdbu.add_brand(ins)
            else:
                log.info('Skipping add new brand %r', name)
