from flask_restful import Resource
from flask import request
from price.modules.imp_price.services import Services
from price.modules.imp_price.ma_schemas import (ImpCatalogPageStatusSchema)

import logging
log = logging.getLogger(__name__)


class ImpPriceTest(Resource):
    def get(self):
        s = Services()
        result = s.get_pages(7)
        return {
            'ans': 'HelloWorld',
            'daa': result
        }


class ImpCatalogProduct(Resource):
    def get(self, imp_catalog_page_id, scan_date):
        log.debug('Get info about catalog_product_id: {} for date: {}'.format(imp_catalog_page_id, scan_date))
        s = Services()
        # result = s.get_product_by_id(imp_catalog_page_id, scan_date)
        return s.get_product_by_id(imp_catalog_page_id, scan_date)


class ImpProductInfo(Resource):
    def get(self, imp_catalog_page_id):
        s = Services()
        return s.get_product_info(imp_catalog_page_id)


class ImpProductImagses(Resource):
    def get(self, imp_catalog_page_id):
        s = Services()
        result = s.get_product_images(imp_catalog_page_id)
        log.debug('Result : %r', result)
        if result:
            return result.images
        else:
            return None


class ImpCatalogPageSearch(Resource):
    def get(self, field, value):
        s = Services()
        # lista = s.search_product_by_category(value)
        # log.info('To jest lista %r', lista)
        return [
            k.imp_catalog_page_id
            for k in s.search_product_by_category(value)
        ]


class ImpCatalogPageStatus(Resource):
    def post(self):
        # , status_type, imp_catalog_page_id):
        s = Services()
        post_data = ImpCatalogPageStatusSchema().load(request.form)
        """
        log.info('request.data: %r', request.data)
        log.info('request.data: %r', request.args)
        log.info('request.data: %r', request.form)
        log.info('request.data: %r', request.json)
        """
        log.info('Post Data: %r', post_data)
        if post_data.get('status_type') == 'category':
            status_id = s.set_catalog_page_status_category(post_data.get('imp_catalog_page_id'))
        elif post_data.get('status_type') == 'brand':
            status_id = s.set_catalog_page_status_brand(post_data.get('imp_catalog_page_id'))
        return {
            'status_type': post_data.get('status_type'),
            'status_id': status_id
        }
