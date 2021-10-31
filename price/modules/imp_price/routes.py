from price.extension import api
# from flask_restful import Resource

from price.modules.imp_price.endpoints import Test



api.add_resource(Test, '/test')
