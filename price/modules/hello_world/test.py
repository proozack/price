from flask_restful import Resource

import logging
log = logging.getLogger(__name__)


class HelloWorld(Resource):
    def get(self):
        return {
            'ans': 'HelloWorld'
        }
