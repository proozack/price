from app.utils.local_type import Ofert

import logging
log = logging.getLogger(__name__)


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


class ELadyPl():

    def __init__(self, response_object):
        self.response_object = response_object

    def parse_entity(self, soup):
        title = NotImplemented
        price = NotImplemented
        currency = NotImplemented
        address = NotImplemented
        img = NotImplemented

        log.info('\n________________________________________\nTo jest SOUP %r', soup)
        raw_ent = soup.findAll(attrs={"class": "prodimage f-row"})
        log.info('\n________________________________________\nTo jest raw_ent %r', raw_ent)
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

        o = Ofert(title, price, currency, address, img)
        log.info('\n________________________________________\nTo jest O: %r', o)
        return o

    def get_next(self, soup):
        next_page_raw = soup.findAll(attrs={"class": "next"})
        if next_page_raw:
            result = next_page_raw[0].get('href')
            if result:
                return ''.join([self.response_object.protocol, '://', self.response_object.domain, result])


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
