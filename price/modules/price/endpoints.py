from flask_restful import Resource
from price.modules.price.services import Services


import logging
log = logging.getLogger(__name__)


class PriceTest(Resource):
    def get(self):
        # s = Services()
        # result = []
        # result = s.list_category()
        # result = s.get_pages(7)
        return {
            'answert': 'HelloWorld',
            'data': 'test'
        }


class PriceEntryPoint(Resource):
    def get(self, entry_point_id):
        s = Services()
        return s.get_shop_id(entry_point_id)


class PriceShop(Resource):
    def get(self, shop_id):
        s = Services()
        return s.get_shop_name(shop_id)


class PriceMenu(Resource):
    def get(self):
        s = Services()
        return s.get_price_menu()
