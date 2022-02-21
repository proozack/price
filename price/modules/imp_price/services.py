from datetime import datetime
import pprint
from price.utils.dict_utils import sa_obj_to_dict
from price.modules.imp_price.db_utils import (
    ImpCatalogPageDbU,
    ImpProductPriceDbU,
    ImpProductPageDbU,
    ImpCatalogPageStatusDbU
)
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

    def get_pages(self, shop_id=None, url_str=None, entry_point_id=None):
        icpdbu = ImpCatalogPageDbU()
        if shop_id is not None:
            log.info('Searching by URL shop_id: {}'.format(shop_id))
            return icpdbu.get_url_by_shop_id(shop_id)
        elif url_str is not None:
            log.info('Searching by URL string: {}'.format(url_str))
            return icpdbu.get_not_processing_url(url_str)
        else:
            log.info('Searching by EpID: {}'.format(entry_point_id))
            return icpdbu.get_not_processing_url(None, entry_point_id)

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

    def get_processed_entry_points(self):
        icpdbu = ImpCatalogPageDbU()
        return icpdbu.get_processed_entry_points()

    def get_tagging_product(self, imp_catalog_page_id):
        icpdbu = ImpCatalogPageDbU()
        return sa_obj_to_dict(
            icpdbu.get_tagging_product(imp_catalog_page_id)
        )

    def get_list_pages(self, imp_catalog_page_id=None, creation_date=None):
        icpdbu = ImpCatalogPageDbU()
        for imp_catalog_page_id in icpdbu.get_imp_catalog_page(imp_catalog_page_id, creation_date):
            yield imp_catalog_page_id

    def get_unprocessed_pages(self, scan_date=None):
        icpdbu = ImpCatalogPageDbU()
        for imp_catalog_page_id in icpdbu.get_unprocessed_pages(scan_date):
            yield imp_catalog_page_id

    def set_catalog_page_status_category(self, imp_catalog_page_id):
        icpsdbu = ImpCatalogPageStatusDbU()
        return icpsdbu.c_set_specific_category(imp_catalog_page_id)

    def set_catalog_page_status_brand(self, imp_catalog_page_id):
        icpsdbu = ImpCatalogPageStatusDbU()
        return icpsdbu.c_set_specific_brand(imp_catalog_page_id)

    def search_product_by_category(self, category):
        icp = ImpCatalogPageDbU()
        return icp.search_product_by_category(category)

    def get_product_by_id(self, imp_catalog_page_id, scan_date):
        icp = ImpCatalogPageDbU()
        return icp.get_product_by_id(imp_catalog_page_id, scan_date)

    def get_product_images(self, imp_catalog_page_id):
        ipp = ImpProductPageDbU()
        return ipp.get_images_by_imp_catalog_page_id(imp_catalog_page_id)

    def get_all_price_for_catalog_page(self, scan_date=None):
        icp = ImpCatalogPageDbU()
        return icp.get_all_price_for_catalog_page(scan_date)

    def get_product_info(self, imp_catalog_page_id):
        ipp = ImpProductPageDbU()
        return ipp.get_product_info(imp_catalog_page_id)
