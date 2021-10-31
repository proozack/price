from datetime import datetime
import pprint
from price.modules.imp_price.db_utils import ImpCatalogPageDbU, ImpProductPriceDbU, ImpProductPageDbU
from price.modules.price.db_utils import OfertDbUtils
from price.modules.imp_price.utils.page_downloader import PageDownloader, get_parser_by_domain
from price.modules.imp_price.local_types import ProductPage

import logging
log = logging.getLogger(__name__)


class Services():
    def copy_product_to_imp(self, scan_date=datetime.now().date()) -> int:
        on = 0
        odbu = OfertDbUtils()
        icpdbu = ImpCatalogPageDbU()
        ippdbu = ImpProductPriceDbU()
        for on, ofert in enumerate(odbu.get_all_ofert_by_creation_date(scan_date)):
            if ofert.url and ofert.entry_point_id and ofert.title is not None:
                # log.debug("Parse product {} {}".format(on, ofert.url))
                imp_catalog_page_id = icpdbu.c_add_catalog_page(
                    ofert.entry_point_id,
                    ofert.url, ofert.title,
                    ofert.image,
                    ofert.manufacturer
                )
                ippdbu.c_add_product_price(
                    imp_catalog_page_id,
                    ofert.price,
                    ofert.currency,
                    ofert.creation_date.date()
                )
        return on

    def copu_all_produc_to_imp(self):
        odbu = OfertDbUtils()
        for on, scan_date in enumerate(odbu.get_all_date()):
            log.info(('{} Scan Date: {}').format(on, scan_date))
            then = datetime.now()
            count = self.copy_product_to_imp(scan_date)
            now = datetime.now()
            duration = now - then
            log.info('Copy {} objects in {} s.'.format(count, duration.total_seconds()))


    def try_download_page(self, url, show_log=False):
        pp = pprint.PrettyPrinter(indent=4)
        product_page = self.get_product_page(url, show_log)
        log.info('Result dict:')
        log.info('________ {}'.format(pp.pformat(product_page.get_local_field_as_dict())))
        

    def get_product_page(self, url=None, show_log=False) -> ProductPage:
        log.debug('Try dwonload page: {}'.format(url))
        pd = PageDownloader(url)
        result = pd.download_page()
        page_body = result.get_contents()
        if show_log:
            log.info('Page Body: \n {}'.format(page_body))
        parser = get_parser_by_domain(result)
        pd.parse_page(page_body, parser.get_product_page)
        product_page = pd.get_data()
        return product_page 

    def get_pages(self, shop_id=None, url_str=None):
        icpdbu = ImpCatalogPageDbU()
        if shop_id is None:
            return icpdbu.get_not_processing_url(url_str)
        return icpdbu.get_url_by_shop_id(shop_id)

    def process_product_pages(self, result):
        ippdbu = ImpProductPageDbU()
        log.warning('Proces url: {}'.format(result.get('url')))
        pp = self.get_product_page(result.get('url'))
        pp.imp_catalog_page_id = result.get('id')
        if pp.deleted:
            icpdbu = ImpCatalogPageDbU()
            log.info('Deactivete product_id {}'.format(pp.imp_catalog_page_id))
            icpdbu.deactivate_product(pp.imp_catalog_page_id)
        else:
            ippdbu.c_save_product_page(pp)

    def parase_product_pages(self, shop_id):
        for result in self.get_pages(shop_id):
            param = {
                'id': result.id,
                'url': result.url
            }
            self.process_product_pages(param)
            break

