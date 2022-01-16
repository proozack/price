import datetime
import random
from flask_restful import Resource
from flask import render_template, make_response
from price.modules.product.services import Services
from price.utils.rest_util import get


import logging
log = logging.getLogger(__name__)


class Config():
    REAL_URL = 'http://py2.eu:7001/'
    STATIC_URL = 'http://py2.eu:7003/'


class ProductTest(Resource):
    def get(self):
        s = Services()
        # result = []
        result = s.list_category()
        # result = s.get_pages(7)
        return {
            'answert': 'HelloWorld',
            'data': result
        }


class ProductDef(Resource):
    def get(self):
        s = Services()
        result = s.list_product_def()
        return {
            'answert': 'ProductDef',
            'data': result
        }


class ProductCatalog(Resource):
    def get(self, category, page_id):
        s = Services()
        meta_category_id = get('http://127.0.0.1:7001/definitions_meta_category/{}'.format(category)).get('id')
        result = s.get_list_product_by_meta_category_id(meta_category_id, '2022-01-06')
        count = result.count()
        log.debug('Result %r', result)
        wyn = result.paginate(page_id, 32)

        template = render_template(
            'she_category.html',
            resource={
                'title': '2py.eu',
                'icon_path': ''.join([Config.STATIC_URL, 'logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'category': category,
                'page': page_id,
                'count': count,
                'max_page': int(count/32) if count % 32 == 0 else int(count/32) + 1
            },
            entities=wyn.items,
            new_menu=get('http://127.0.0.1:7001/menu'),
            menu=get('http://127.0.0.1:7001/price_menu'),
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class ProductViews(Resource):
    def get(self, brand, name):
        s = Services()
        result = s.get_product_for_view(brand, name, '2022-01-06')
        log.info('Result %r ', result)
        template = render_template(
            'product_views.html',
            resource={
                'title': '2py.eu',
                'product_title': name,
                'product_brand': brand,
                'icon_path': ''.join([Config.STATIC_URL, 'logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'category': '',  # entry_point.url,
            },
            entities=result,
            new_menu=get('http://127.0.0.1:7001/menu'),
            menu=get('http://127.0.0.1:7001/price_menu'),
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp


class ProductCatalogImg(Resource):
    def get(self, name, brand):
        s = Services()
        result = s.get_image_for_catalog(name, brand)
        return {
            'product_definition_id': result.id,
            'path_thumbs': result.path_thumbs,
        }


class Start(Resource):
    def get(self):
        s = Services()
        meta_category_id = random.randrange(1, 20, 1)
        now = datetime.datetime.now()
        result = s.get_list_product_by_meta_category_id(meta_category_id, '2022-01-06')
        wyn = result.paginate(1, 32)
        template = render_template(
            'index.html',
            resource={
                'title': 'Price - reale value',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'description': 'Friendly prices search engine',
                'year': now.year,
                'category': get('http://127.0.0.1:7001/definitions_meta_category/{}'.format(meta_category_id)).get('name'), # noqa E501
            },
            entities=wyn.items,
            new_menu=get('http://127.0.0.1:7001/menu'),
            menu=get('http://127.0.0.1:7001/price_menu'),
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp
