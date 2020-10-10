from app.utils.local_type import Ofert
from app.utils.url_utils import UrlUtils
from requests import Request, Session
import re
import json
from app.utils.bs_tools import get_soup_from_url

import logging
log = logging.getLogger(__name__)


class WwwTestCom():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('article', {"class": "productBox_product"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        log.info('RAW:\n%r\n_____________\n', soup)
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        log.info('SOUP:\n%r', soup)
        return None


class IntimitiPl():
    def __init__(self, response_object):
        # self.soup = soup
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        price = soup.findAll(attrs={"itemprop": "price"})
        title = soup.findAll(attrs={"itemprop": "name"})
        currency = soup.findAll(attrs={"itemprop": "priceCurrency"})
        image = soup.findAll('img')

        address = soup.findAll(attrs={"data-correct": "product-photo"})
        if len(address) > 0:
            adr = address[0].get('href')

        image_list = []
        for img in image:
            im = img.get('src')
            if im:
                image_list.append(im)
        raw_manufacturer = soup.findAll(attrs={'class': 'producer-name'})
        if raw_manufacturer:
            temp_manufacturer = raw_manufacturer[0].findAll('a')
            if temp_manufacturer:
                manufacturer = temp_manufacturer[0].get('title')

        return Ofert(
            title[0].text,
            float(price[0].get('content')),
            currency[0].text.strip(),
            adr,
            image_list[0],
            manufacturer
        )
        """
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o
        """

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "pagination-next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class OhsoPl():
    def __init__(self, response_object):
        # self.soup = soup
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented

        raw_price = soup.findAll(attrs={'class': "cat_price"})
        if len(raw_price) > 0:
            price_as_str = raw_price[0].text.strip()
            tab_price = price_as_str.split(' ')
            price = tab_price[0]
            currency = tab_price[1]

        raw_url = soup.findAll(attrs={'class': 'href_onclick'})
        if raw_url:
            url = raw_url[0].get('href')
            temp_tab = url.split(',')
            ile_pol = len(temp_tab)
            temp_tab.pop(ile_pol-1)
            url = ','.join(temp_tab)
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])

            tmp_img = raw_url[0].findAll('img')
            if tmp_img:
                temp_image = tmp_img[0]

                if temp_image:
                    log.info('IMG : %r', temp_image)
                    title = temp_image.get('alt')
                    img = temp_image.get('data-original-desktop')

        o = Ofert(title, price, currency, address, img)
        log.info('O: %r', o)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "angle-right"})
        if next_page_raw:
            next_page_tmp = next_page_raw[0].findAll('a')
            if next_page_tmp:
                log.info('To jest next_page_raw %r', next_page_tmp[0].get('href'))
                result = next_page_tmp[0].get('href')
                return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class DomodiPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        price = soup.findAll(attrs={"class": "dm-price-light__regular"})
        raw_title = soup.findAll(attrs={"data-ga-label": "product_name"})
        raw_img = soup.findAll('img')

        if len(price) > 0:
            tab = price[0].text.split(' ')
            price = tab[0]
            currency = tab[1]

            href = raw_title[0].get('href')
            if href:
                address = ''.join([self.response_object.clear_url, href])
                img = raw_img[0].get('data-original')
                if img:
                    img = ':'.join([self.response_object.protocol, raw_img[0].get('data-original'), ])

                    return Ofert(
                        raw_title[0].text,
                        float(price),
                        currency.strip(),
                        address,
                        img
                    )

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"aria-label": "Następna strona"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class NoshamePl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        """
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        """
        title = None
        price = None
        currency = None
        address = None
        img = None
        manufacturer = NotImplemented

        raw_ent = soup.findAll(attrs={"class": "shb-product-list-title"})
        if raw_ent:
            test = raw_ent[0].findAll('a')
            address = test[0].get('href')
            title = test[0].get('title')

        raw_img = soup.findAll('img')
        if raw_img:
            tmp_img = raw_img[0].get('src')
            img = tmp_img

        # shb-product-list-new-price"
        m_price = soup.findAll(attrs={"class": "shb-product-list-new-price"})
        raw_price = soup.findAll('span')

        if m_price or raw_price:
            if m_price:
                price_as_str = m_price[0].text.strip()
            elif raw_price:
                price_as_str = raw_price[0].text.strip()

            # price_as_str = raw_price[0].text.strip()
            tab_price = price_as_str.split(' ')
            price = tab_price[0]
            currency = tab_price[1]

        manufacturer = 'noshame'
        if title and address and img:
            o = Ofert(title, price, currency, address, img, manufacturer)
            return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "next"})
        if next_page_raw:
            tmp = next_page_raw[0].findAll('a')
            if tmp:
                result = tmp[0].get('href')
                return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class SwiatbieliznyPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = None
        price = None
        currency = None
        address = None
        img = None

        log.info('\n________________________________________\nTo jest soup %r', soup)
        log.info('\n________________________________________\n')

        raw_url = soup.findAll('a')
        if raw_url:
            tmp_url = raw_url[0].get('href')
            address = ''.join([self.response_object.clear_url, tmp_url])
        # log.info('\n________________________________________\nTo jest raw_url %r', tmp_url)

        raw_title = soup.findAll(attrs={'class': "name"})
        if len(raw_title) > 0:
            title = raw_title[0].text.strip()

        raw_price = soup.findAll(attrs={'class': "price"})
        if len(raw_price) > 0:
            price_as_str = raw_price[0].text.strip()
            tab_price = price_as_str.split(' ')
            price = tab_price[0]
            currency = tab_price[1]

        o = Ofert(title, price, currency, address, img)
        log.info('\n\n To jest o: %r', o)
        return NotImplemented

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class IntymnaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_ent = soup.findAll(attrs={"class": "href_onclick"})

        if raw_ent:
            url = raw_ent[0].get('href')
            temp_tab = url.split(',')
            ile_pol = len(temp_tab)
            temp_tab.pop(ile_pol-1)
            url = ','.join(temp_tab)
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])

            image = raw_ent[0].findAll(attrs={"class": "podgl_min podgl_min_lazy"})
            if image:
                temp_image = image[0]
                if temp_image:
                    img = temp_image.get('rel')

        # raw_ent = soup#.findAll(attrs={'class': 'href_onclick'})

        raw_price = soup.findAll(attrs={'class': "cat_price"})
        if len(raw_price) > 0:
            price_as_str = raw_price[0].text.strip()
            tab_price = price_as_str.split(' ')
            price = tab_price[0]
            currency = tab_price[1]

        raw_title = soup.findAll(attrs={"class": "cat_prod_name"})
        if len(raw_title) > 0:
            temp_title = raw_title[0].findAll('a')
            if temp_title:
                title = temp_title[0].text
        raw_manufacturer = soup.findAll(attrs={'class': 'cat_man'})
        if raw_manufacturer:
            manufacturer = raw_manufacturer[0].text

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll(attrs={"class": "paginator"})
        if raw_pagination:
            field = raw_pagination[0].findAll(attrs={"class", "angle-right"})
            if field:
                link = field[0].findAll('a')
                if link:
                    result = link[0].get('href')
                    return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class ByannPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_ent = soup.findAll(attrs={"class": "prodimage f-row"})
        if raw_ent:
            title = raw_ent[0].get('title')
            result = raw_ent[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
            raw_img = raw_ent[0].findAll('img')
            if raw_img:
                tmp_img = raw_img[0].get('data-src')
                img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
        raw_price = soup.findAll('em')
        if raw_price:
            tmp_price = raw_price[1].text
            price_as_str = tmp_price.strip()
            tab_price = price_as_str.split('\xa0')
            price = tab_price[0].replace(',', '.')
            currency = tab_price[1]
        raw_manufacturer = soup.findAll(attrs={"class": "brand"})
        if raw_manufacturer:
            manufacturer = raw_manufacturer[0].get('title')

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll(attrs={'class': 'last'})
        if raw_pagination:
            field = raw_pagination[1].findAll('a')
            if field:
                result = field[0].get('href')
                link = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return link


class KontriPl():

    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_ent = soup.findAll(attrs={"class": "showProduct"})
        if raw_ent:
            result = raw_ent[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
            raw_title = raw_ent[0].findAll('img')
            title = raw_title[0].get('alt')
            img = raw_title[0].get('src')
        raw_price = soup.findAll(attrs={'title': 'gross'})
        if raw_price:
            price_as_str = raw_price[0].text
            tab_price = price_as_str.split('\xa0')
            price = tab_price[0].replace(',', '.')
            currency = tab_price[1]
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll(attrs={'class': 'next'})
        if raw_pagination:
            field = raw_pagination[1].findAll('a')
            if field:
                result = field[0].get('href')
                link = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return link


class SensualePl():

    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_ent = soup.findAll(attrs={"class": "prodimage f-row"})
        if raw_ent:
            title = raw_ent[0].get('title')
            result = raw_ent[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
            raw_img = raw_ent[0].findAll('img')
            if raw_img:
                tmp_img = raw_img[0].get('data-src')
                img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
        raw_price = soup.findAll('em')
        if raw_price:
            tmp_price = raw_price[1].text
            price_as_str = tmp_price.strip()
            tab_price = price_as_str.split('\xa0')
            price = tab_price[0].replace(',', '.')
            currency = tab_price[1]
        raw_manufacturer = soup.findAll(attrs={"class": "brand"})
        if raw_manufacturer:
            manufacturer = raw_manufacturer[0].get('title')
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll(attrs={'class': 'last'})
        if raw_pagination:
            field = raw_pagination[1].findAll('a')
            if field:
                result = field[0].get('href')
                link = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return link


class UlubionabieliznaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_url = soup.findAll(attrs={"class": "sl_add"})
        if raw_url:
            url = raw_url[0].get('data-link')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            title = raw_url[0].get('data-name')
            price_as_str = raw_url[0].get('data-price')
            tab_price = price_as_str.split(' ')
            price = tab_price[0].replace(',', '.')
            currency = tab_price[1]
            raw_img = raw_url[0].get('data-src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_img])
            manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            if result:
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return path


class MagicznabieliznaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_tab_url = soup.findAll('a')
        if raw_tab_url:
            address = raw_tab_url[0].get('href')
            title = raw_tab_url[0].get('title')
            raw_tab_img = raw_tab_url[0].findAll('img')
            if raw_tab_img:
                img = raw_tab_img[0].get('src')
        raw_tab_price = soup.findAll(attrs={"class": "price_view_span"})
        if raw_tab_price:
            raw_price_1 = raw_tab_price[0].findAll(attrs={"class": "price_1"})
            price_1 = raw_price_1[0].text
            raw_price_2 = raw_tab_price[0].findAll(attrs={"class": "price_2"})
            price_2 = raw_price_2[0].text
            price = ''.join([price_1, price_2]).replace(',', '.')
            raw_currency = raw_tab_price[0].findAll(attrs={"class": "currency"})
            currency = raw_currency[0].text.strip()
        raf_manufacturer = soup.findAll('img')
        if len(raf_manufacturer) > 2:
            manufacturer = raf_manufacturer[2].get('alt')
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "li_listing li_listing_next fl pointer"})
        if next_page_raw:
            raw_a_np = next_page_raw[0].findAll('a')
            if raw_a_np:
                result = raw_a_np[0].get('href')
                # path = ''.join([self.response_object.protocol,'://', self.response_object.domain, result])
                return result


class EkskluzywnaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_tab = soup.findAll('article')
        if raw_tab:
            address = raw_tab[0].get('data-url')

        raw_img = soup.findAll('img')
        if raw_img:
            img = raw_img[0].get('src')
            title = raw_img[0].get('title')
        raw_price = soup.findAll(attrs={'itemprop': 'price'})
        if raw_price:
            price = raw_price[0].get('content')
        raw_currency = soup.findAll(attrs={'itemprop': 'priceCurrency'})
        if raw_currency:
            currency = raw_currency[0].get('content')
        manufacturer = None

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "pagination-next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            path = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
            return path


class EldarPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a')
        if raw_string:
            url = raw_string[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            title = raw_string[0].get('title')
            raw_img = raw_string[0].findAll('img')
            if raw_img:
                img = raw_img[0].get('data-src')
        raw_price = soup.findAll(attrs={"class": "price"})
        if raw_price:
            tmp_price = raw_price[0].text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = 'eldar'
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "--next"})
        if next_page_raw:
            raw_a = next_page_raw[0].findAll('a')
            if raw_a:
                result = raw_a[0].get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return path


class AnaisApparelPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a')
        if raw_string:
            url = raw_string[0].get('href')
            address = url
            title = raw_string[0].get('title')
        raw_img = soup.findAll('img')
        if raw_img:
            img = raw_img[0].get('src')

        raw_price = soup.findAll(attrs={"class": "price"})
        if raw_price:
            tmp_price = raw_price[0].text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = 'anais'

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "pagination_next"})
        if next_page_raw:
            raw_a = next_page_raw[0].findAll('a')
            if raw_a:
                result = raw_a[0].get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
                return path


class MorgantiPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a')
        if raw_string:
            url = raw_string[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', url])
            title = raw_string[1].text.strip()
        raw_img = soup.findAll('img')
        if raw_img:
            tmp_img = raw_img[0].get('src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', tmp_img])

        raw_price = soup.findAll(attrs={"class": "price"})
        if raw_price:
            raw_strong = raw_price[0].findAll('strong')
            if raw_strong:
                tmp_price = raw_strong[0].text.split(' ')
                price = tmp_price[0].strip()
                currency = tmp_price[1].strip()
        manufacturer = None

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={'class': 'next'})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            if result:
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', result])
                return path


class DobraBieliznaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a')
        if raw_string:
            url = raw_string[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            title = raw_string[1].text.strip()
        raw_img = soup.findAll('img')
        if raw_img:
            tmp_img = raw_img[0].get('data-src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])

        raw_price = soup.findAll(attrs={'class': 'price'})
        if raw_price:
            raw_strong = raw_price[0].findAll('em')
            if raw_strong:
                tmp_price = raw_strong[0].text.split('\xa0')
                price = tmp_price[0].replace(',', '.').strip()
                currency = tmp_price[1].strip()
        raw_manufacturer = soup.findAll(attrs={'class': 'brand'})
        if raw_manufacturer:
            manufacturer = raw_manufacturer[0].text.lower().strip()
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll('li', {'class': 'last'})
        if next_page_raw:
            result = next_page_raw[1].findAll('a')
            if result:
                url = result[0].get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
                return path


class WwwJagnaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a')
        if raw_string:
            url = raw_string[0].get('href')
            address = url
        raw_img = soup.findAll('img', {'class': 'prod_lst_img'})
        if raw_img:
            tmp_img = raw_img[0].get('src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', tmp_img])
            title = raw_img[0].get('alt').strip()
        raw_price = soup.findAll('span', {'class': 'NewPrice'})
        if raw_price:
            tmp_price = raw_price[0].text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll('td', {'class': 'nextButton'})
        if next_page_raw:
            result = next_page_raw[1].findAll('a')
            if result:
                log.info('Result %r', result)
                path = result[0].get('href')
                return path


class AtrakcyjnaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        # log.info('Soup %r\n____________', soup)
        raw_string = soup.findAll('a', {'class': 'product-name'})
        if raw_string:
            tmp_url = raw_string[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_url])
        raw_img = soup.findAll('img', {'class': 'b-lazy'})
        if raw_img:
            tmp_img = raw_img[0].get('data-src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
            title = raw_img[0].get('alt').strip()
        raw_price = soup.findAll('span', {'class': 'price'})
        if raw_price:
            tmp_price = raw_price[0].text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.find('ul', {'class': 'pagination'})
        if next_page_raw:
            a = next_page_raw.find('i', {'class': 'icon-angle-right'})
            raw_a = a.find_parent('a')
            if raw_a:
                url = raw_a.get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
                return path


class WwwMisternaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        # log.info('Soup %r\n____________', soup)
        raw_string = soup.findAll('a', {'class': 'product-name'})
        if raw_string:
            tmp_url = raw_string[0].get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_url])
        raw_img = soup.findAll('img', {'class': 'b-lazy'})
        if raw_img:
            tmp_img = raw_img[0].get('data-src')
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
            title = raw_img[0].get('alt').strip()
        raw_price = soup.findAll('span', {'class': 'price'})
        if raw_price:
            tmp_price = raw_price[0].text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.find('div', {'class': 't-strony'})
        if next_page_raw:
            switcher = False
            # log.info('next_page_raw: %r', next_page_raw)
            for child in next_page_raw.children:
                if child:
                    b_found = child.find('b')
                    log.info('To jest b_found %r  %r \n (%r)',  b_found, child, dir(b_found))
                    if b_found:
                        switcher = True

                # if child != '':
                #    log.info('next_page_raw: %r', child)

                log.info('Switcher %r', switcher)
            """
            a = next_page_raw.find('i', {'class': 'icon-angle-right'})
            raw_a = a.find_parent('a')
            if raw_a:
                url = raw_a.get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
                return path
            """


class SkrytePl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_string = soup.findAll('a', {'class': 'product_img_link'})
        if raw_string:
            tmp_url = raw_string[0].get('href')
            address = tmp_url
            title = raw_string[0].get('title').strip()
        raw_img = soup.findAll('div', {'class': 'swiper-zoom-container'})
        if raw_img:
            tmp_img = raw_img[0].findAll('img')
            if tmp_img:
                img = tmp_img[0].get('src')
        raw_price = soup.findAll('span', {'class': 'price'})
        if raw_price:
            price = raw_price[0].text.strip().replace('zł', '')
            currency = 'zł'
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll('li', {'class': 'pagination_next'})
        if next_page_raw:
            result = next_page_raw[0].findAll('a')
            if result:
                # log.info('Result %r', result)
                url = result[0].get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
                return path
        return None


class WwwBielComPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_img = soup.findAll('img')
        if raw_img:
            img = raw_img[0].get('src')
        raw_title = soup.findAll('div', {'class': 'name'})
        if raw_title:
            temp_ti = raw_title[0].find('a')
            title = temp_ti.text.strip()
            address = temp_ti.get('href')
        raw_manufacturer = soup.findAll('div', {'class': 'brand'})
        if raw_manufacturer:
            temp_ma = raw_manufacturer[0].find('a')
            manufacturer = temp_ma.text.strip()
        raw_price = soup.findAll('div', {'class': 'price'})
        if raw_price:
            raw_pr = raw_price[0].find('bdi')
            temp_price = raw_pr.text.split('\xa0')
            price = temp_price[0].strip().replace(' ', '')
            currency = temp_price[1].strip()

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll('a', {'class': 'next'})
        if raw_pagination:
            result = raw_pagination[0].get('href')
            link = result
            return link
        return None


class AllBieliznaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_title = soup.find('div', {'class': 'product-name'})
        if raw_title:
            raw_url = raw_title.find('a')
            url = raw_url.get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            title = raw_url.get('title').strip()
        raw_price = soup.find('span', {'class': 'core_priceFormat'})
        if raw_price:
            price = raw_price.get('data-price').strip()
            currency = 'zł'
        raw_image = soup.find('img', {'class': 'product-main-img'})
        if raw_image:
            tmp_img = raw_image.get('src').strip()
            img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.findAll('i', {'class': 'fa-chevron-right'})
        if raw_pagination:
            raw_a = raw_pagination[0].find_parent('a')
            if raw_a:
                url = raw_a.get('href')
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
                return path
        return None


class WwwDlazmyslowPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_item = soup.find('div', {'class': 'rowimg'})
        if raw_item:
            raw_img = raw_item.find('img')
            if raw_img:
                img = raw_img.get('src')
                title = raw_img.get('alt').strip()
            raw_url = raw_item.find('a')
            if raw_url:
                url = raw_url.get('href')
                address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
        raw_price = soup.find('span', {'class': 'cena'})
        if raw_price:
            tmp_price = raw_price.text.split(' ')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('img', {'alt': 'Następna'})
        if raw_pagination:
            raw_a = raw_pagination.find_parent('a')
            if raw_a:
                url = raw_a.get('href')
                uu = UrlUtils(self.response_object.url)
                tmp_url = uu.get_attr_from_url(self.response_object.url)
                if tmp_url:
                    tmp_url = ''.join(['?', tmp_url])
                    tmp_url = self.response_object.url.replace(tmp_url, '')
                    path = ''.join([tmp_url, url])
                else:
                    path = ''.join([self.response_object.url, url])
                return path
        return None


class WwwAstratexPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('article', {"class": "productBox_product"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        currency = 'zł'
        manufacturer = None
        raw_price = soup.find('p', {'class': 'price'})
        if raw_price:
            tmp_price = raw_price.text.split(' ')
            price = tmp_price[0].strip().replace(',', '.')
        raw_price_a = soup.find('p', {'class': 'priceAction'})
        if raw_price_a:
            tmp_price_a = raw_price_a.find('strong')
            tprice = tmp_price_a.text.split(' ')
            price = tprice[0].strip().replace(',', '.')
        raw_img = soup.find('img', {'class': 'product-image-main'})
        if raw_img:
            img = raw_img.get('src')
            title = raw_img.get('alt')
        raw_url = soup.find('a', {'data-ga-action': 'productClick'})
        if raw_url:
            url = raw_url.get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'next'})
        if raw_pagination:
            url = raw_pagination.get('href')
            path = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            return path
        return None


class ClodiPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('article', {"class": "product-miniature"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw = soup.find('div', {'class': 'thumbnail-container'})
        if raw:
            raw_img = raw.find('img', {'class': 'lazy'})
            if raw_img:
                img = raw_img.get('data-full-size-image-url')
                title = raw_img.get('alt')
            raw_url = raw.find('a', {'class': 'thumbnail'})
            if raw_url:
                url = raw_url.get('href')
                address = ''.join([self.response_object.protocol, ':', url])

            raw_price = raw.find('div', {'class': 'price'})
            if raw_price:
                log.info('Raw_price %r ', raw_price)
                tmp_price = raw_price.text.split(' ')
                if tmp_price:
                    price = tmp_price[0].replace(',', '.').strip()
                    currency = tmp_price[1].strip()
            manufacturer = None

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'next'})
        if raw_pagination:
            path = raw_pagination.get('href')
            return path
        return None


class WwwHurtowniaOlenkaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('div', {"class": "Okno"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw = soup.find('div', {'class': 'AnimacjaZobacz'})
        if raw:
            raw_title = raw.find('div', {'class': 'ProdCena'})
            if raw_title:
                raw_url = raw_title.find('a')
                if raw_url:
                    address = raw_url.get('href')
                    title = raw_url.text.strip()
                raw_price = raw_title.find('span', {'class': 'Cena'})
                if raw_price:
                    raw_price = raw_price.text.split(' ')
                    price = raw_price[0].replace(',', '.').strip()
                    currency = raw_price[1].strip()
                raw_img = raw.find('img', {'class': 'Zdjecie'})
                if raw_img:
                    tmp_img = raw_img.get('src')
                    img = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', tmp_img])
                raw_manufacturer = raw.find('ul', {'class': 'ListaOpisowa'})
                if raw_manufacturer:
                    tmp_manufacturer = raw_manufacturer.find('a')
                    manufacturer = tmp_manufacturer.text.strip()
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        is_active = False
        raw_pagination = soup.find('div', {'class': 'IndexStron'})
        if raw_pagination:
            raw_a = raw_pagination.find_all('a')
            for a in raw_a:
                if is_active:
                    url = a.get('href')
                    return url
                if a.has_attr('class'):
                    is_active = True
        return None


class SklepkostarPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('div', {"class": "product-inner"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_img = soup.find('img', {'loading': 'lazy'})
        if raw_img:
            title = raw_img.get('alt')
            img = raw_img.get('src')
        raw_url = soup.find('a', {'class': 'woocommerce-LoopProduct-link'})
        if raw_url:
            address = raw_url.get('href')
        raw_price = soup.find_all('bdi')
        if raw_price:
            for tmp_price in raw_price:
                price = tmp_price.text.replace('zł', '').strip()
                currency = 'zł'
        manufacturer = 'kostar'
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'next'})
        if raw_pagination:
            link = raw_pagination.get('href')
            return link
        return None


class ObsessiveCom():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('li', {"class": "item"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw = soup.find('a', {'class': 'product-image'})
        if raw:
            address = raw.get('href')
            title = raw.get('title')
        raw_img = soup.find('img', {'class': 'img-responsive'})
        if raw_img:
            img = raw_img.get('data-desktop')
        raw_price = soup.find('span', {'class': 'price'})
        if raw_price:
            temp_price = raw_price.text.split('\xa0')
            price = temp_price[0].replace(',', '.').strip()
            currency = temp_price[1].strip()
        manufacturer = 'obsessive'
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'next'})
        if raw_pagination:
            link = raw_pagination.get('href')
            return link
        return None


class ModivoPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        raw = soup.find('div', {'class': 'is-offerGrid'})
        for field in raw.find_all('div', {"class": 'c-offerBox_inner'}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_price = soup.find('div', {'class': 'a-price'})
        if raw_price:
            price = raw_price.text.replace('zł', '').replace(',', '.').replace(' ', '').strip()
            currency = 'zł'
        raw_a_price = soup.find('div', {'class': 'is-promoPrice'})
        if raw_a_price:
            price = raw_a_price.text.replace('zł', '').replace(',', '.').replace(' ', '').strip()
        raw = soup.find('div', {'class': 'c-offerBox_data'})
        if raw:
            raw_url = raw.find('a')
            tmp_url = raw_url.get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_url])
            manufacturer = raw_url.text.strip()
        raw_img = soup.find('div', {'class', 'c-offerBox_photo'})

        if raw_img:
            tmp_img = raw_img.find('img')
            if tmp_img:
                if tmp_img.has_attr('src'):
                    t_img = tmp_img.get('src')
                else:
                    t_img = tmp_img.get('data-src').split('|')
                    t_img = t_img[0]
                img = ''.join([self.response_object.protocol, '://', self.response_object.domain, t_img])
        raw_title = soup.find('div', {'class': ['a-typo', 'is-text']})
        if raw_title:
            title = raw_title.text.strip()
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'is-nextLink'})
        if raw_pagination:
            link = raw_pagination.get('href')
            return link
        return None


class WwwELadyPl():

    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        id_products = []
        results = soup.find_all('div', {'data-type': 'product'})
        if results:
            for result in results:
                product_id = result.get('data-product-id')
                id_products.append(int(product_id))
        str_list = []
        for product_id in id_products:
            str_list.append('{}{}'.format('data%5BProduct%5D%5Bid%5D%5B%5D=', product_id))
        post_data = '&'.join(str_list)
        header = {
            'Accept': '*/*',
            'User-Hash': 'aa0d1789178c78840d9f2ede5593517a0b45392b',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36', # noqa E501
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': ',https://www.e-lady.pl',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': self.response_object.url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        url = 'https://www.e-lady.pl/ceny'
        s = Session()
        req = Request('POST', url, data=post_data, headers=header)
        prepped = s.prepare_request(req)
        resp = s.send(prepped)
        self.ceny = resp.json()

        for field in soup.find_all('div', {"class": "product-box"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_url = soup.find('a', {'data-type': 'product-url'})
        if raw_url:
            title = raw_url.get('title')
            result = raw_url.get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, result])
        raw_img = soup.find('img')
        if raw_img:
            img = raw_img.get('src')
        product_id = soup.get('data-product-id')
        price = self.ceny[product_id]['price'].replace('zł', '').replace(',', '.').strip()
        currency = 'zł'
        manufacturer = self.ceny[product_id].get('producer', None)
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            if result:
                return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


class WwwEsotiqCom():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        results = soup.find('script', text=re.compile(".*categorypageConfig.*"))
        a = results.contents[0]
        b = a.replace('var categorypageConfig =', '')
        c = b.strip()
        i = json.loads(c[:-1])
        for p in i.get('products'):
            result = {
                'price': p.get('discount_price') if p.get('discount_price') else p.get('price'),
                'address': p.get('url'),
                'img':  p.get('image').get('src'),
                'title': p.get('image').get('alt'),
                'manufacturer': 'esotiq',
            }
            yield result

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        temp = soup.get('price').split(' ')
        title = soup.get('title')
        price = temp[0]
        currency = temp[1].lower()
        address = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', soup.get('address')])
        img = ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', soup.get('img')])
        manufacturer = soup.get('manufacturer')

        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        if self.response_object.url[-2:] == '=1':
            path = self.response_object.url
        else:
            path = ''.join([self.response_object.url, '?strona=1'])
        path = path[:-1]
        inc = 1
        url = ''.join([path, str(inc)])
        soup = get_soup_from_url(url)
        results = soup.find('script', text=re.compile(".*categorypageConfig.*"))
        if not results:
            return None
        a = results.contents[0]
        b = a.replace('var categorypageConfig =', '')
        c = b.strip()
        i = json.loads(c[:-1])
        if len(i.get('products')):
            inc = inc + 1
            url = ''.join([path, str(inc)])
            return url
        return None


class Www2HmCom():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('div', {"class": "item-details"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        log.info('RAW:\n%r\n_____________\n', soup)
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        log.info('SOUP:\n%r', soup)
        return None


class EroprezentPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('li', {"class": "product"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_title = soup.find('h2', {'class': 'woocommerce-loop-product__title'})
        if raw_title:
            title = raw_title.text.strip()
        raw_url = soup.find('a', {'class': 'woocommerce-LoopProduct-link'})
        if raw_url:
            address = raw_url.get('href')
        raw_img = soup.find('img', {'loading': 'lazy'})
        if raw_img:
            img = raw_img.get('data-src')

        raw_prices = soup.find_all('span', {'class': 'woocommerce-Price-amount'})
        if raw_prices:
            for raw_price in raw_prices:
                tmp_price = raw_price.text.split('\xa0')
                price = tmp_price[0].strip().replace(',', '.')
                currency = tmp_price[1].strip()
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'class': 'next'})
        if raw_pagination:
            link = raw_pagination.get('href')
            return link
        return None


class NbieliznaPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('article', {"class": "productBox_product"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        log.info('RAW:\n%r\n_____________\n', soup)
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        log.info('SOUP:\n%r', soup)
        return None
