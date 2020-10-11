import requests
from bs4 import BeautifulSoup
from app.modules.price.db_utils import BrandDbUtils, OfertDbUtils, KeyWordLinkDbUtils, TagWordLinkDbUtils
from app.utils.url_utils import UrlUtils

import logging
log = logging.getLogger(__name__)


class TagTools():
    def __init__(self):
        self.twldu = TagWordLinkDbUtils()
        self.tags_list = self.twldu.get_tags()

    def search_tag(self, title):
        found_tag = []
        for tag in self.tags_list:
            result = title.find(tag)
            if result >= 0:
                found_tag.append(tag)

        return found_tag if found_tag else None

    def remove_tag_from_title(self, title, tag_list) -> str:
        tag_list.sort(key=len, reverse=True)
        for tag in tag_list:
            title = title.replace(tag if tag else '', '').strip()
        return (
            title,
            tag_list
        )


class SizeTools():
    def __init__(self):
        self.size_list = [
            's',
            'm',
            'l',
            'xl',
            'xxl',
            'xxxl',
        ]

    def search_size_in_string(self, name):
        found_size = []
        tab_name = name.split(' ')
        for size in self.size_list:
            if size in tab_name:
                found_size.append(size)
        return found_size

    def remove_size_from_string(self, name, size_list):
        tab_name = name.split(' ')
        for size in size_list:
            tab_name.remove(size)
        return ' '.join(tab_name)


class CategoryTools():
    def __init__(self, category_id):
        self.kwldu = KeyWordLinkDbUtils()
        self.category_id = category_id
        self.category_synonyms = self.kwldu.get_all_word()

    def search_catgeory_name(self, title):
        find_category = ''
        find_category_id = None
        for synonym, category_id, word_id in self.category_synonyms:
            wyn = title.lower().find(synonym)
            if wyn >= 0:
                if len(find_category) <= len(synonym):
                    find_category = synonym
                    find_category_id = category_id
        return (
            find_category if find_category != '' else None,
            find_category_id
        )

    def remove_category_from_title(self, title, category_name):
        if not category_name:
            category_name = ''
        return (
            title.lower().replace(
                category_name,
                ''
            ).strip().capitalize(),
            None if category_name == '' else category_name,
        )


class OfertTools():
    def __init__(self):
        pass

    def parse_title_by_category(self, category_id):
        p = BrandTools()
        o = OfertDbUtils()
        for ofert in o.get_all_ofert_by_category(category_id):
            name = ofert[1]
            manufacturer = ofert[4]
            parsed_title = p.remove_brand_from_title(name, manufacturer)
            yield parsed_title


class BrandTools():
    def __init__(self):
        self.bdbu = BrandDbUtils()
        self.brands_list = self.bdbu.get_all_brand_as_list()

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

    def search_brand(self, title):
        found_brand = ''
        for brand in self.brands_list:
            result = title.lower().find(brand)
            if result >= 0:
                if len(found_brand) <= len(brand):
                    found_brand = brand
        return found_brand if found_brand != '' else None

    def remove_brand_from_title(self, title, manufacturer):
        result = self.search_brand(title)
        new_title = title.lower().replace(result if result else '', '').strip()
        return (
            new_title.capitalize(),
            None if result == '' else result,
            manufacturer
        )
