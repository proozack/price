from app.utils.local_type import Ofert, TempProduct
from app.modules.price.db_utils import OfertDbUtils, CategoryDbUtils, ProductDbUtils
from app.modules.price.tools import BrandTools, CategoryTools
from slugify import slugify

import logging
log = logging.getLogger(__name__)


class MatchProduct():
    def __init__(self):
        self.pt = BrandTools()
        self.pdbu = ProductDbUtils()
        self.skip_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~'] # noqa E501

    def parase_all_ofert(self, ofert_id=None, shop_id=None) -> Ofert:
        odbu = OfertDbUtils()
        # log.info('To jest oferta %r', ofert_id)
        for ofert in odbu.get_all_oferts(ofert_id, shop_id):
            yield ofert

    def parse_offert(self, ofert):
        tp = TempProduct(**self.sa_obj_to_dict(ofert))
        tp = self._parse_title(tp)
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # remove all bad char

        # search tags
        # search bad words
        #

        # log.info(pp.pprint(tp.get_dict()))
        log.info('Manufacturer: %r', tp.manufacturer)
        log.info('Tp object %r', tp.get_dict())
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
        self._save_product(tp)
        log.info('____________________________________________')

    def _parse_title(self, tp):
        tp = self._remove_bad_chars_in_title(tp)
        tp = self._serch_manufacturer_in_title(tp)
        tp = self._serch_category_in_title(tp)
        return tp

    def parse_image(self, image):
        pass

    def sa_obj_to_dict(self, sa_object):
        result = {}
        for field in sa_object._fields:
            result[field] = getattr(sa_object, field, None)
        return result

    def _serch_manufacturer_in_title(self, tp_object: TempProduct) -> TempProduct:

        manufacturer = self.pt.search_brand(tp_object.title)
        title = self.pt.remove_brand_from_title(tp_object.title, manufacturer)
        tp_object.title = title[0]
        if not tp_object.manufacturer:
            tp_object.manufacturer = manufacturer
            return tp_object
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

    def _remove_bad_chars_in_title(self, tp_object: TempProduct) -> TempProduct:
        temp_title = tp_object.title
        for char in self.skip_characters:
            temp_title = temp_title.replace(char, ' ')
        if temp_title != tp_object.title:
            log.info('Chaneg title from {} to {}'.format(tp_object.title, temp_title))
            tp_object.title = temp_title
        return tp_object

    def _save_product(self, tp_object):
        # log.info('Save object %r', tp_object.get_dict())
        log.info(' ### Zapisuję ###')
        tp_object.add_field('slug', slugify(' '.join([tp_object.manufacturer, tp_object.title])))
        self.pdbu.add_product(tp_object)
