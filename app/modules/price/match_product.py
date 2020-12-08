from app.utils.local_type import Ofert, TempProduct
from app.modules.price.db_utils import OfertDbUtils, CategoryDbUtils, ProductDbUtils, ProductVersionDbUtils, BrandDbUtils
from app.modules.price.tools import BrandTools, CategoryTools, TagTools, SizeTools
from app.utils.string_utils import StringUtils
from slugify import slugify
import pprint

import logging
log = logging.getLogger(__name__)


class MatchProduct():
    def __init__(self):
        self.pt = BrandTools()
        self.pdbu = ProductDbUtils()
        self.st = SizeTools()
        self.tt = TagTools()
        self.skip_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~'] # noqa E501

    def parse_offert(self, ofert):
        tp = TempProduct(**self.sa_obj_to_dict(ofert))
        pp = pprint.PrettyPrinter(indent=4)
        log.info('Przetwarzam %r', pp.pprint(tp.get_dict()))
        tp = self._parse_title(tp)
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # remove all bad char

        # search tags
        # search bad words
        #

        # log.info(pp.pprint(tp.get_dict()))
        # log.info('Manufacturer: %r', tp.manufacturer)
        # log.info('Tp object %r', tp.get_dict())
        # log.info('%r', tp)
        # log.info('%r', new_title)
        # if exist url in ProductShopUrl
        #   add
        # else
        #   skip
        #
        # search controol_sum image in product_images_list
        # if exist control_sum:
        #   associate with the product
        #
        # parse in title product name
        # registy new product
        # remove product from ofert
        #
        # log.info('____________________________________________')
        return tp

    def _parse_title(self, tp):
        tp = self._remove_bad_chars_in_title(tp)
        tp = self._search_size_from_title(tp)
        tp = self._serch_manufacturer_in_title(tp)
        tp = self._serch_category_in_title(tp)
        tp = self._search_tags_in_title(tp)
        tp = self._remove_space(tp)
        tp = self._search_product(tp)
        tp = self._search_product_version(tp)
        if not tp.brand_id:
            bdbu = BrandDbUtils() 
            tp.brand_id = bdbu.get_brand_by_product_name(tp.title)
        return tp

    def parse_image(self, image):
        pass

    def sa_obj_to_dict(self, sa_object):
        result = {}
        for field in sa_object._fields:
            result[field] = getattr(sa_object, field, None)
        return result

    def _search_tags_in_title(self, tp_object: TempProduct) -> TempProduct:
        tags_list = self.tt.search_tag(tp_object.title)
        if tags_list:
            title = self.tt.remove_tag_from_title(tp_object.title, tags_list)
            if tp_object.title != title:
                log.info('Tags: Change title from {} to {}'.format(tp_object.title, title[0]))
                tp_object.title = title[0]
                tp_object.add_field('tag', title[1])
        if not hasattr(tp_object, 'tag'):
            tp_object.add_field('tag', [])
        return tp_object

    def _serch_manufacturer_in_title(self, tp_object: TempProduct) -> TempProduct:
        su = StringUtils()
        if not tp_object.manufacturer:
            # obsłużyc przypadek gdy produkt nie ma producenta w tyule ani w nei był na stronie katalogowej
            # można spórbowac w url'u produktu
            manufacturer = self.pt.search_brand(tp_object.title)
            log.info('Response manu %r ', manufacturer)
            if manufacturer:
                title = self.pt.remove_brand_from_title(tp_object.title, manufacturer)
                if tp_object.title != title[0]:
                    log.info('Manufacturer: Change title from {} to {}'.format(tp_object.title, title[0]))
                    tp_object.title = title[0]
            else:
                log.info('Manufacturer: search brand in url %r', tp_object.url)
                manufacturer = self.pt.search_brand(' '.join(su.multisplit_string(tp_object.url, lower=False)))
                log.info('Response %r', manufacturer)

            #można dodać poszukiwanie też po url zdjęcia oraz finalnie po nazwie produktu
            if len(manufacturer):
                log.info('Set new manufacturer {}'.format(manufacturer))
                tp_object.manufacturer = manufacturer[1]
                tp_object.add_field('brand_id', manufacturer[0])
            else:
                tp_object.add_field('brand_id', None)

        else:
            manufacturer = self.pt.search_brand(tp_object.title)
            title = self.pt.remove_brand_from_title(tp_object.title, manufacturer)
            if tp_object.title != title[0]:
                log.info('Manufacturer: Change title from {} to {}'.format(tp_object.title, title[0]))
                tp_object.title = title[0]

            bdbu = BrandDbUtils() 
            tp_object.add_field('brand_id', bdbu.get_brand_id_by_name(tp_object.manufacturer.lower()))



        return tp_object

    def _serch_category_in_title(Self, tp_object: TempProduct) -> TempProduct:
        ct = CategoryTools(tp_object.category_id)
        category_synonyms, category_id = ct.search_catgeory_name(tp_object.title)
        if category_synonyms and category_id:
            title = ct.remove_category_from_title(tp_object.title, category_synonyms)
            tp_object.title = title[0]
            if category_id != tp_object.category_id:
                cdbu = CategoryDbUtils()
                log.info('Get category name by id %r', category_id)
                new_category_name = cdbu.get_category_name_by_id(category_id)
                log.info(
                    'Change category from {}(id:{}) to {}(id:{})'.format(
                        tp_object.category_name,
                        tp_object.category_id,
                        new_category_name,
                        category_id
                    )
                )
                tp_object.category_id = category_id
                tp_object.category_name = new_category_name
                return tp_object
        return tp_object

    def _search_size_from_title(self, tp_object: TempProduct) -> TempProduct:
        size_list = self.st.search_size_in_string(tp_object.title)
        if size_list:
            title = self.st.remove_size_from_string(tp_object.title, size_list)
            if tp_object.title != title:
                log.info('Size: Change title from {} to {}'.format(tp_object.title, title))
                tp_object.title = title
                tp_object.add_field('size', size_list)
        return tp_object

    def _remove_bad_chars_in_title(self, tp_object: TempProduct) -> TempProduct:
        temp_title = tp_object.title
        for char in self.skip_characters:
            temp_title = temp_title.replace(char, ' ')
        if temp_title != tp_object.title:
            log.info('BadChar: Change title from {} to {}'.format(tp_object.title, temp_title))
            tp_object.title = temp_title
        return tp_object

    def _remove_space(self, tp_object: TempProduct) -> TempProduct:
        tab = tp_object.title.split(' ')
        if '' in tab:
            tab.remove('')
        new_title = ' '.join(tab)
        if new_title != tp_object.title:
            log.info('RemoveSpace: Change title from {} to {}'.format(tp_object.title, new_title))
            tp_object.title = new_title
        return tp_object

    def _search_product(self, tp_object: TempProduct) -> TempProduct:
        ppdu = ProductDbUtils()
        product_id = ppdu.if_product_exists(
            tp_object.title,
            tp_object.brand_id,
            tp_object.category_id
        )
        tp_object.add_field('product_id', product_id)
        return tp_object

    def _search_product_version(self, tp_object: TempProduct) -> TempProduct:
        log.info('%r', tp_object.get_dict())
        pvdbu = ProductVersionDbUtils()
        tags_count = len(tp_object.tag)
        tag_id_list = [
            id
            for id, name in tp_object.tag
        ]
        result = pvdbu.search_product_by_tags(tp_object.product_id, tag_id_list)
        if result is None:
            product_version_id = pvdbu.search_version_by_products_name(
                tp_object.title,
                tp_object.brand_id,
                tp_object.category_id,
                tp_object.url
            )
            tp_object.add_field('product_version_id', product_version_id)
            log.info('SV: searcg by name %r', tp_object.title)
        elif result.count == tags_count:
            tp_object.add_field('product_version_id', result.id)
            log.info('SV: searcg by tag list')
        else:
            tp_object.add_field('product_version_id', none)
            log.info('SV: add empty version_id field')
        return tp_object
