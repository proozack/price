from flask_restful import Resource


from price.modules.imp_price.services import Services


import logging
log = logging.getLogger(__name__)


class Test(Resource):
    def get(self):
        s = Services()
        result = s.get_pages(7)
        return {
            'ans': 'HelloWorld',
            'daa': result
        }
