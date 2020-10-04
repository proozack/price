import pprint
from app.utils.local_type import Ofert, TempProduct
from app.modules.price.db_utils import OfertDbUtils
from app.modules.price.tools import ProductTools, CategoryTools

import logging
log = logging.getLogger(__name__)


class MatchProduct():
    def __init__(self):
        self.pt = ProductTools()

    def parase_all_ofert(self, ofert_id=None) -> Ofert:
        odbu = OfertDbUtils()
        log.info('To jest oferta %r', ofert_id)
        for ofert in odbu.get_all_oferts(ofert_id):
            yield ofert

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

    def _serch_category_in_title(Self, tp_object: TempProduct) -> TempProduct:
        ct = CategoryTools(tp_object.category_id)
        # category_synonyms = ct.search_catgeory_name(tp_object.title)
        title = ct.remove_category_from_title(tp_object.title)
        tp_object.title = title[0]
        return tp_object

    def parse_offert(self, ofert):
        pp = pprint.PrettyPrinter(indent=4)
        tp = TempProduct(**self.sa_obj_to_dict(ofert))
        tp = self._serch_manufacturer_in_title(tp)
        tp = self._serch_category_in_title(tp)

        log.info(pp.pprint(tp.get_dict()))
        log.info('Manufacturer: %r', tp.manufacturer)
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

    def parse_title(self, title):
        # remove brand ame from title
        # remove produt type from title
        # remove tags from title
        # get rest as a product name
        pass

    def parse_image(self, image):
        pass
