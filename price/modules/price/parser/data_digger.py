from requests import Request, Session
import re
import json
from price.utils.local_type import Ofert
from price.utils.url_utils import UrlUtils
from price.utils.bs_tools import get_soup_from_url
from price.modules.imp_price.local_types import ProductPage

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

    def get_product_page(self, soup):
        pp = ProductPage()
        return pp


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

        raw_url = soup.findAll('a')
        if raw_url:
            tmp_url = raw_url[0].get('href')
            address = ''.join([self.response_object.clear_url, tmp_url])

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

    def get_product_page(self, soup):
        pp = ProductPage()
        return pp


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

    def get_product_page(self, soup):
        pp = ProductPage()

        product_not_exist = soup.find('span', {'class': 'produnavail'})
        if product_not_exist:
            log.warning('Product not exist: %r ', product_not_exist.text)
            pp.deleted = True
            pp.active = False
            return pp

        product_deleted = soup.find('div', {'class': 'search-error-head'})
        if product_deleted:
            log.warning('Product has been deleted %r ', product_deleted.text.strip())
            pp.deleted = True
            pp.active = False
            return pp

        product_path = soup.find('ul', {'class': 'bcrumbs'})
        if product_path:
            pp.attributes = {}
            pp.attributes.update(
                {
                    'product_path': product_path.text.replace('\n', '/')
                }
            )

        pp.title = soup.find('title').text
        pp.description = soup.find('div', {'class': 'produkt-opis'}).text.replace('\n', '').replace('\r', '')
        pp.brand = soup.find('span', {'class': 'text-uppercase'}).text

        raw_category = soup.find('span', {'class': 'link_gksp_nazwa'})
        if raw_category:
            pp.category = raw_category.text

        raw_color = soup.findAll('img', {'class': 'liniakolor_popup_thumb_img'})
        pp.color = []
        for tmp_color in raw_color:
            pp.color.append(tmp_color.get('title'))
        if len(pp.color) == 0:
            raw_color = soup.find('span', {'class', 'proddeflineinputdef'})
            if raw_color:
                pp.color.append(raw_color.text)
            else:
                pp.color = []

        raw_size = soup.find('select', {'class': 'input_size'})
        lista = []
        if raw_size:
            for tmp_size in raw_size.findAll('option'):
                if tmp_size.text != 'wybierz rozmiar':
                    lista.append(tmp_size.text)
        pp.size = lista

        raw_composition = soup.find('div', {'class': 'produkt-material'})
        if raw_composition:
            raw_composition = raw_composition.text.replace('Materiał:', '').strip()
            pp.composition = raw_composition
        raw_img = soup.findAll('a', {'class', 'mview'})
        img = []
        for temp in raw_img:
            img.append({
                'big': temp.get('data-image'),
                'thumbs': temp.find('img').get('src')
            })
        pp.images = img
        return pp


class WwwIntymnaPl(IntymnaPl):
    pass


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
        # log.info('SOUP %r', soup)
        raw_img = soup.find('img', {'class': 'b-lazy'})
        tmp_img = raw_img.get('data-src')
        img = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_img])
        title = raw_img.get('alt').strip()
        raw_price = soup.find('span', {'class': 'price'})
        tmp_price = raw_price.text.split(' ')
        price = tmp_price[0].strip().replace(',', '.')
        currency = tmp_price[1].strip()
        manufacturer = title.split(' ')[0]
        raw_url = soup.find('a', {'class': 'product-name'})
        tmp_url = raw_url.get('href')
        address = ''.join([self.response_object.protocol, '://', self.response_object.domain, tmp_url])
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        link = None
        raw_pagination = soup.find('ul', {'class': 'pagination'})
        if raw_pagination:
            temp = raw_pagination.findAll('a')
            if temp:
                if len(temp) == 1:
                    is_active = temp[0].find('i', {'class': 'icon-angle-right'})
                    if is_active:
                        link = temp[0].get('href')
                        link = ''.join([self.response_object.protocol, '://', self.response_object.domain, link])
                else:
                    link = temp[1].get('href')
                    link = ''.join([self.response_object.protocol, '://', self.response_object.domain, link])
        return link

    def get_product_page(self, soup):
        pp = ProductPage()
        raw_brand = soup.find('a', {'class': 'firmlogo'})
        if raw_brand is None:
            log.info('Product not found')
            pp.deleted = True
            pp.active = False
            return pp
        pp.brand = raw_brand.find('img').get('title').strip().lower()

        raw_category = soup.find('div', {'class': 'list_wrapper'})
        list_cat = [
            i.text.strip().lower()
            for i in raw_category('li')
        ]
        count_cat = len(list_cat)
        pp.category = list_cat[count_cat-2]

        path = '/'.join(list_cat)
        pp.attributes = {'product_path': path}

        raw_title = soup.find('div', {'class': 'projector_navigation'})
        raw_title = raw_title.find('h1')
        pp.title = raw_title.text

        raw_color = soup.find('div', {'class': 'product_section versions'})
        if raw_color:
            pp.color = [
                color.get('alt')
                for color in raw_color.findAll('img')
            ]
        else:
            pp.color = []

        raw_size = soup.find('div', {'class': 'product_section sizes'})
        tmp_size = raw_size.findAll('a')
        pp.size = [
            rs.text
            for rs in tmp_size
        ]
        raw_desc = soup.find('div', {'class': 'projector_longdescription_sub'})
        pp.description = raw_desc.text

        pp.composition = None

        img = []
        img_list = soup.findAll('a', {'class': 'projector_medium_image'})
        for raw_img in img_list:
            raw_thumbs = raw_img.find('img').get('data-lazy')
            img.append({
                'big': ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_img.get('href')]), # noqa E501
                'thumbs': ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_thumbs]) # Noqa E501
            })
        pp.images = img
        return pp


class WwwKontriPl(KontriPl):
    pass


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

    def get_product_page(self, soup):
        pp = ProductPage()

        raw_title = soup.find('div', {'class': 'projector_navigation'})
        if raw_title is None:
            log.info('Product not found')
            pp.deleted = True
            pp.active = False
            return pp

        pp.title = raw_title.text.strip()
        raw_description = soup.find('div', {'class': 'projector_description'})
        if raw_description:
            pp.description = raw_description.text.strip()
        else:
            pp.description = None

        raw_brand = soup.find('a', {'class': 'brand'})
        if raw_brand:
            pp.brand = raw_brand.text.strip()
        else:
            pp.brand = None
        raw_path = soup.find('div', {'class': 'breadcrumbs'})
        nl = []
        for temp_path in raw_path.findAll('li'):
            nl.append(temp_path.text.strip())
        pp.category = nl[-2:-1][0]
        path = '/'.join(nl)
        pp.attributes = {'product_path': path}
        pp.color = []
        pp.size = []
        pp.composition = None
        raw_color_size = soup.findAll('div', {'class': 'product_section_sub'})
        if len(raw_color_size) == 3:
            raw_color = []
            raw_size = raw_color_size[0]
        elif len(raw_color_size) == 4:
            raw_color = raw_color_size[0]
            raw_size = raw_color_size[1]
        else:
            raw_color = []
            raw_size = []

        if raw_color:
            colors = []
            for color in raw_color.findAll('a'):
                colors.append(color.get('title').strip())
            pp.color = colors

        if raw_size:
            size = []
            for sizes in raw_size.findAll('a'):
                size.append(sizes.find('b').text.strip())
            pp.size = size

        img = []
        for raw_img in soup.findAll('img', {'class': 'photo'}):
            img.append({
                'big': ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_img.get('data-zoom-image')]), # noqa E501
                'thumbs': ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_img.get('src')]) # Noqa E501
            })
        pp.images = img
        return pp


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

        raw_price = soup.find('span', {'itemprop': 'price'})
        price = raw_price.get('content')

        # temp_title = soup.find('h2', {'class': 'product-name'})
        currency = soup.find('span', {'class': 'currency_pinfo'}).text.lower().strip()
        raw_img = soup.find('img', {'class': 'rc_button'})
        img = raw_img.get('src')
        title = raw_img.get('alt').lower()
        temp_man = soup.find('div', {'itemprop': 'manufacturer'})
        raw_man = temp_man.find('img')
        if raw_man is not None:
            manufacturer = raw_man.get('alt').lower()
        else:
            manufacturer = None
        raw_address = soup.find('a', {'itemprop': 'url'})
        address = raw_address.get('href')
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        """
        next_page_raw = soup.findAll(attrs={"class": "li_listing li_listing_next fl pointer"})
        if next_page_raw:
            raw_a_np = next_page_raw[0].findAll('a')
            if raw_a_np:
                result = raw_a_np[0].get('href')
                # path = ''.join([self.response_object.protocol,'://', self.response_object.domain, result])
                return result
        """
        next_page_raw = soup.find('div', {'class', 'pagination'})
        all_page = next_page_raw.findAll('a')
        last_page = all_page[-1]
        if last_page.text == '»':
            next_page = last_page.get('href')
            path = ''.join([self.response_object.protocol, '://', self.response_object.domain, next_page])
            return path
        else:
            return None

    def get_product_page(self, soup):
        pp = ProductPage()
        not_exists = soup.find('div', {'class': 'container-title'})
        if not_exists is not None and not_exists.text.strip() == 'Zaawansowane szukanie':
            pp.deleted = True
            pp.active = False
            return pp

        raw_brand = soup.find('div', {'class': 'pinfo-producer'})
        pp.brand = raw_brand.find('a').text
        pp.title = soup.find('h1', {'class': 'pinfo-name'}).text
        raw_path = soup.find('ul', {'class': 'breadcrumb-ajax'}).text.strip()

        nl = []
        list_ent = raw_path.split('\n')
        for element in list_ent:
            if element not in ('\n', ' ', '\t', ''):
                # log.info('Element %r', element)
                nl.append(element)
        path = '/'.join(nl)

        pp.attributes = {'product_path': path}
        pp.description = soup.find('div', {'class': 'product-description'}).text.strip()
        raw_img = soup.findAll('a', {'class': 'slideHref'})
        img = []

        for tmp_img in raw_img:
            para_img = tmp_img.find('img')
            img.append({
                'big': tmp_img.get('href'),
                'thumbs': para_img.get('src')
                # log.info('IMG: %r', ele.get('src'))
            })
        pp.images = img
        pp.category = nl[-2:-1][0]
        pp.color = None
        pp.composition = None
        pp.size = None
        return pp


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

        raw_title = soup.find('img', {'class': 'lazyImg'})
        if raw_title:
            img = raw_title.get('data-src')
            title = raw_title.get('alt')

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

    def get_product_page(self, soup):
        pp = ProductPage()
        # log.info('Soup %r', soup)
        raw_title = soup.find('h1', {'class': 'pinfo-name'})
        if raw_title is None:
            log.warning('Product not exist: Product not found')
            pp.deleted = True
            pp.active = False
            return pp

        pp.title = raw_title.text.strip()
        raw_brand = soup.find('span', {'class': 'pinfo-producer__text'})
        if raw_brand:
            raw_brand = raw_brand.text.split(':')
            pp.brand = raw_brand[1].strip()
        else:
            pp.brand = None
        raw_path = soup.find('ul', {'class': 'breadcrumb-ajax'})
        nl = []
        for ele in raw_path.text.split('\n'):
            if ele not in ('', ' ', '\n', '\t'):
                nl.append(ele)
        pp.category = nl[-2:-1][0]
        nl = '/'.join(nl)
        pp.attributes = {'product_path': nl}

        raw_description = soup.find('div', {'class': 'product-description'})
        if raw_description:
            list_des = raw_description.findAll('p')
            descr = []
            for des in list_des:
                descr.append(des.text.strip())
            pp.description = ' '.join(descr)
        else:
            pp.description = None

        img = []
        for ele in soup.findAll('img', {'itemprop': 'image'}):
            img.append({
                'big': ele.get('data-zoom-image'),
                'thumbs': ele.get('src')
            })

        pp.images = img
        pp.color = None
        pp.composition = None
        pp.size = None
        return pp


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
                img = ''.join([self.response_object.protocol, '://', self.response_object.domain, img])
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


class WwwMorgantiPl():
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

    def get_product_page(self, soup):
        pp = ProductPage()

        is_active_raw = soup.find('p', {'class', 'noprod'})
        if is_active_raw and is_active_raw.text.strip() == 'Produkt aktualnie niedostępny':
            log.info('Product not found')
            pp.deleted = True
            pp.active = False
            return pp

        raw_brand = soup.find('img', {'itemprop': 'logo'})
        if raw_brand:
            pp.brand = raw_brand.get('alt').strip().lower()
        else:
            pp.brand = None

        raw_title = soup.find('h1', {'itemprop': 'name'})
        pp.title = raw_title.text.strip().lower()

        raw_desc = soup.find('div', {'class': 'desc-text'})
        if raw_desc:
            pp.description = raw_desc.text.strip()
        else:
            pp.description = None

        raw_size = soup.find('', {'name': 'wariant_grupa2'})
        sizes = raw_size.findAll('option')
        pp.size = []
        for no, s in enumerate(sizes):
            if no != 0:
                pp.size.append(s.text.strip().lower())

        raw_color = soup.find('', {'name': 'wariant_grupa1'})
        colors = raw_color.findAll('option')
        pp.color = []
        for no, c in enumerate(colors):
            if no != 0:
                pp.color.append(c.text.strip().lower())

        raw_cat = soup.find('div', {'id': 'breadcrumbs'})
        path = []
        for cat in raw_cat.findAll('li'):
            path.append(cat.text.replace('»', '').strip().lower())
        pp.category = path[-1]

        nl = '/'.join(path)
        pp.attributes = {'product_path': nl}

        raw_img = soup.findAll('a', {'class': 'cloud-zoom-gallery'})
        img = []
        for tmp_img in raw_img:
            thumbs = tmp_img.get('rel2')
            small = thumbs.split(':')[2]
            small = small.replace('"', '').replace("'", '').strip()
            img.append({
                'big': ''.join([self.response_object.protocol, '://', self.response_object.domain,'/', tmp_img.get('href')]), # noqa E501
                'thumbs': ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', small]),
            })
        pp.images = img
        pp.composition = None

        return pp


class MorgantiPl(WwwMorgantiPl):
    pass


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

    # def get_product_page(self, soup):
    #     pp = ProductPage()
    #     return pp


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

    def parse_catalog(self, soup):
        log.info('Soup %r', soup)
        for field in soup.find_all('article', {"class": "product-miniature"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_title = soup.find('div', {'class': 'product-name'})

        log.info('Sopu %r', soup)

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

    def get_product_page(self, soup):
        pp = ProductPage()

        not_exists = soup.find('div', {'class': 'product-archive-desc'})
        if not_exists is not None and not_exists.text.strip() == 'Tego produktu już nie ma w sprzedaży':
            log.warning('Product not exist: %r ', not_exists.text)
            pp.deleted = True
            pp.active = False
            return pp

        raw_title = soup.find('div', {'id': 'head-line'})
        pp.title = raw_title.text.strip()
        pp.size = []
        raw_size = soup.find('div', {'class': 'size'})
        if raw_size:
            for size in raw_size.findAll('option'):
                if size.text not in ('wybierz'):
                    pp.size.append(size.text.strip())
        raw_color = soup.find('div', {'class': 'colors'})
        pp.color = []
        for color in raw_color.findAll('label'):
            pp.color.append(color.get('title'))
        raw_brand = soup.find('a', {'class': 'producer-link'})
        pp.brand = raw_brand.text.strip()
        raw_composition = soup.find('div', {'class': 'param-row'})
        if raw_composition:
            pp.composition = raw_composition.text.strip().replace('Materiał', '')
        else:
            pp.composition = None
        raw_description = soup.find('div', {'id':  'DetailLegend'})
        pp.description = raw_description.find('div').text.strip()

        attributes = soup.find('nav', {'id': 'CategoryPar'})
        nl = []
        for ele in attributes.text.split('\n'):
            if ele not in ('', ' ', '\n', '\t'):
                nl.append(ele)
        pp.category = nl[-2:-1][0]
        nl = '/'.join(nl)
        pp.attributes = {'product_path': nl}

        raw_img = soup.find('div', {'id': 'DetailImgGalerySub'})
        img = []
        for tmp_img in raw_img.findAll('a'):
            temp = tmp_img.find('img')
            img.append({
                'big': tmp_img.get('href'),
                'thumbs': temp.get('src')
            })
        pp.images = img
        return pp


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
                    if tmp_manufacturer:
                        manufacturer = tmp_manufacturer.text.strip()
                    else:
                        manufacturer = None
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

    def get_product_page(self, soup):
        pp = ProductPage()

        not_exists = soup.find('h1', {'class': 'StrNaglowek'})
        if not_exists is not None and not_exists.text.strip() == 'Brak danych do wyświetlenia':
            log.info('Not found: %r', not_exists.text.strip())
            pp.deleted = True
            pp.active = False
            return pp

        raw_title = soup.find('h1', {'itemprop': 'name'})
        pp.title = raw_title.text.strip()

        raw_brand = soup.find('strong', {'itemprop': 'brand'})
        if raw_brand:
            pp.brand = raw_brand.get('content')
        else:
            pp.brand = None

        raw_description = soup.find('div', {'itemprop': 'description'})
        pp.description = raw_description.text.strip()

        raw_path = soup.find('div', {'id': 'Nawigacja'})
        nl = []
        for ele in raw_path.text.split('»'):
            if ele not in ('', ' ', '\n', '\t'):
                nl.append(ele.strip())
        pp.category = nl[-2:-1][0]
        nl = '/'.join(nl)
        pp.attributes = {'product_path': nl}
        pp.composition = None
        pp.color = None
        pp.size = None
        img = []
        raw_img = soup.find('div', {'id': 'ZdjeciaProduktu'})
        for tmp_img in raw_img.findAll('a'):
            log.info('Raw img %r', tmp_img.get('href'))

            temp = tmp_img.find('img')
            img.append({
                'big': tmp_img.get('href'),
                'thumbs': ''.join([self.response_object.protocol, '://', self.response_object.domain, '/', temp.get('src')]) # noqa E501
            })
        pp.images = img
        return pp


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
                price = price.replace(',', '.')
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
        for field in soup.find_all('div', {"class": "product-box"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_addres = soup.find('a', {'class': 'product-box__image-wrapper'})
        if raw_addres:
            address = raw_addres.get('href')
        raw_img = soup.find('img', {'class': 'product-box__image'})

        if raw_img:
            title = raw_img.get('alt')
            img = raw_img.get('data-src')

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
        """
        raw = soup.find('div', {'class': 'is-offerGrid'})
        if raw:
            for field in raw.find_all('div', {"class": 'c-offerBox_inner'}):
                yield field
        """
        raw = soup.find_all('li', {'class': 'product'})

        if raw:
            for field in raw:
                yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented

        raw_price = soup.find_all('div', {'class': 'price'})
        if raw_price:
            count = len(raw_price)
            temp_price = raw_price[count-1]
            tmp_price = temp_price.text.strip().replace(' ', '').split('\xa0')
            price = tmp_price[0].replace(',', '.').strip()
            currency = tmp_price[1].strip()
        raw_url = soup.find('a', {'class': 'text-link'})
        if raw_url:
            url = raw_url.get('href')
            address = ''.join([self.response_object.protocol, '://', self.response_object.domain, url])
            title = raw_url.get('title')
        raw_img = soup.find('img', {'class': '_imgr'})
        if raw_img:
            img = raw_img.get('src')
        manufacturer = None
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        result = soup.find('span', {'class': 'total-pages'})
        if result:
            tab = result.text.split(' ')
            tab = tab[1]
            uu = UrlUtils()
            atr = uu.get_dicts_from_args(self.response_object.url)
            if atr and atr.get('p'):
                page_num = atr.get('p')
                page_next = int(page_num) + 1
                new_url = self.response_object.url.replace(str(page_num), str(page_next))
            else:
                page_next = '?p=2'
                new_url = ''.join([self.response_object.url, '/', page_next])
            log.info('Test if next page exist %r', new_url)
            soup = get_soup_from_url(new_url)
            results = soup.find('li', {'class': 'product'})
            if results:
                return new_url
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
        log.info('Response %r', soup)
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

        log.info('Soup: %r', soup)

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
        # raw_img = soup.find('img', {'loading': 'lazy'})
        raw_img = soup.find('img', {'class', 'attachment-woocommerce_thumbnail'})
        if raw_img:
            img = raw_img.get('src')

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

    def get_product_page(self, soup):
        pp = ProductPage()
        raw_title = soup.find('h1', {'class': 'product_title'})

        if raw_title is None:
            log.info('Product not found ')
            pp.deleted = True
            pp.active = False
            return pp

        pp.title = raw_title.text.strip()
        raw_path = soup.find('nav', {'class': 'woocommerce-breadcrumb'})
        nl = []
        for ele in raw_path.text.split('/'):
            if ele not in ('', ' ', '\n', '\t'):
                nl.append(ele.strip())
        pp.category = nl[-2:-1][0]
        nl = '/'.join(nl)
        pp.attributes = {'product_path': nl}
        raw_brand = soup.find('table', {'class': 'woocommerce-product-attributes'})
        tmp_brand = raw_brand.find('td', {'class': 'woocommerce-product-attributes-item__value'})
        pp.brand = tmp_brand.text.strip()
        raw_description = soup.find('div', {'class': 'woocommerce-Tabs-panel--description'})
        if raw_description:
            pp.description = raw_description.text.strip()
        else:
            pp.description = None

        raw_img = soup.find('div', {'class': 'woocommerce-product-gallery'})
        img = []
        for tmp_img in raw_img.findAll('a'):
            temp = tmp_img.find('img')
            img.append({
                'big': tmp_img.get('href'),
                'thumbs': temp.get('src')
            })
        pp.images = img
        pp.color = []
        pp.size = []
        pp.composition = None
        return pp


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


class WwwVenusNetPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('li', {"class": "ajax_block_product"}):
            yield field

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented
        manufacturer = NotImplemented
        raw_prices = soup.find('span', {'class': 'price'})
        if raw_prices:
            tmp_price = raw_prices.text.strip().split(' ')
            price = tmp_price[0].strip().replace(',', '.')
            currency = tmp_price[1].strip()

        raw_url = soup.find('a', {'class': 'product_link'})
        if raw_url:
            address = raw_url.get('href')

        raw_img = soup.find('img', {'class': 'img-responsive'})
        if raw_img:
            img = raw_img.get('data-src')
            title = raw_img.get('title')
        raw_brand = soup.find('span', {'class': 'manufacturer_name'})
        if raw_brand:
            manufacturer = raw_brand.text.strip()
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw = soup.find('li', {'class': 'pagination_next'})
        if raw:
            raw_pagination = raw.find('a')
            if raw_pagination:
                path = ''.join([self.response_object.protocol, '://', self.response_object.domain, raw_pagination.get('href')]) # noqa E501
                return path
        return None


class GomezPl():
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


class WwwSisiPl():
    def __init__(self, response_object):
        self.response_object = response_object

    def parse_catalog(self, soup):
        for field in soup.find_all('div', {"class": "productsCont"}):
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
            img = ''.join(
                [
                    self.response_object.protocol,
                    '://',
                    self.response_object.domain,
                    '/',
                    raw_img.get('src')
                ]
            )
            tmp_manufacturer = title.split('-')
            manufacturer = tmp_manufacturer[0].strip()
        raw_url = soup.find('a', {'class': 'productPhoto'})
        if raw_url:
            address = ''.join(
                [
                    self.response_object.protocol,
                    '://',
                    self.response_object.domain,
                    '/',
                    raw_url.get('href')
                ]
            )
        raw_price = soup.find('span', {'class': 'price'})
        if raw_price:
            t_raw_price = soup.find('span', {'class': 'price_pink'})
            if t_raw_price:
                raw_price = t_raw_price
            tmp_price = raw_price.text.split(' ')
            price = tmp_price[0].strip()
            tmp_currency = tmp_price[1].strip().replace(',', '')
            currency = tmp_currency
        raw_new_price = soup.find('span', {'class': 'price_red'})
        if raw_new_price:
            tmp_price = raw_new_price.text.split(' ')
            price = tmp_price[0].strip()
            tmp_currency = tmp_price[1].strip()
            currency = tmp_currency
        o = Ofert(title, price, currency, address, img, manufacturer)
        return o

    def get_next(self, soup):
        raw_pagination = soup.find('a', {'title': 'Następna strona'})

        if raw_pagination:
            return ''.join(
                [
                    self.response_object.protocol,
                    '://',
                    self.response_object.domain,
                    '/',
                    raw_pagination.get('href')
                ]
            )
        return None


class WwwReneePl():
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
