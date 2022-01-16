from price.utils.rest_util import get

import logging
log = logging.getLogger(__name__)


class ProductObj():
    def __init__(self, imp_catalog_page_id, scan_date):

        self.imp_catalog_page_id = imp_catalog_page_id
        self.scan_date = scan_date

        self.name = None
        self.brand = None
        self.shop_id = None
        self.product_url = None
        self.images = []
        self.price = None
        self.currency = None
        self.category = []
        self.entry_point_id = None

    def load_data(self):
        self.get_product_info()
        self.get_shop_id(self.entry_point_id)
        self._get_product_images()
        self._get_tagging_info()

    def get_product_info(self):
        addr = 'http://127.0.0.1:7001/catalog_product/{}/{}'.format(self.imp_catalog_page_id, self.scan_date)
        result = get(addr)
        self.price = result.get('price')
        self.currency = result.get('currency')
        self.product_url = result.get('url')
        self.entry_point_id = result.get('entry_point_id')
        self.images.append({
            'path_big': None,
            'path_thumbs': result.get('img'),
            'img_source': 'imp_catalog_page',
            'orginal_images_id': self.imp_catalog_page_id
        })

    def _get_product_images(self):
        addr = 'http://127.0.0.1:7001/catalog_imagse/{}'.format(self.imp_catalog_page_id)
        result = get(addr)
        if result:
            for img in result:
                self.images.append({
                    'path_big': img.get('big'),
                    'path_thumbs': img.get('thumbs'),
                    'img_source': 'imp_product_page',
                    'orginal_images_id': self.imp_catalog_page_id
                })

    def _get_tagging_info(self):
        addr = 'http://127.0.0.1:7001/tager_result/{}'.format(self.imp_catalog_page_id)
        result = get(addr)
        if result:
            product = result.get('product')
            category = result.get('category')
            self.name = product.get('name')
            self.brand = product.get('brand')
            self.category = [
                cat.get('category')
                for cat in category
            ]

    def get_shop_id(self, entr_point_id):
        addr = 'http://127.0.0.1:7001/entry_point/{}'.format(entr_point_id)
        result = get(addr)
        log.debug('Shop: %r', result)
        if result:
            self.shop_id = result.get('shop_id')
