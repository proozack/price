from flask_restful import Resource
from price.modules.tager.services import Services


import logging
log = logging.getLogger(__name__)


class TagerTest(Resource):
    def get(self):
        s = Services()
        # result = []
        result = s.get_all_context()
        # result = s.get_pages(7)
        return {
            'answert': 'HelloWorld',
            'data': result
        }
