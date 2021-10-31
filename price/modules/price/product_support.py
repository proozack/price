import pprint
from slugify import slugify
from price.modules.price.db_utils import OfertDbUtils, CategoryDbUtils, ProductDbUtils, TagWordLinkDbUtils
from price.utils.local_type import Ofert, TempProduct

import logging
log = logging.getLogger(__name__)

class ProductSupport():
    def __init__(self):
        self.pdbu = ProductDbUtils()

    def parase_all_ofert(self, ofert_id=None, shop_id=None, entry_point_id=None, scan_date=None) -> Ofert:
        odbu = OfertDbUtils()
        # log.info('To jest oferta %r', ofert_id)
        for ofert in odbu.get_all_oferts(ofert_id, shop_id, entry_point_id, scan_date):
            yield ofert

    def save_product(self, tp_object):
        twldu = TagWordLinkDbUtils()
        pp = pprint.PrettyPrinter(indent=4)

        # log.info('Save object %r', tp_object.get_dict())
        log.info(' ### Zapisuję ###')
        log.info('TP: %r', tp_object.manufacturer)
        if tp_object.manufacturer:
            tp_object.add_field('slug', slugify(' '.join([tp_object.manufacturer, tp_object.title])))
            log.info('Save object:\n%r', pp.pprint(tp_object.get_dict()))
        else:
            czy_zapisac = False
            log.info('Manufacturer is empty Skipping registration product {}'.format(tp_object.title))

        czy_zapisac = True

        try:
            if czy_zapisac:
                # todo to poprawić bo używa trzech commitów
                self.pdbu.save_product(tp_object)
            else:
                log.info('Skipping registration product {}'.format(tp_object.title))
        except Exception:
            log.warning('Error', exc_info=True)
