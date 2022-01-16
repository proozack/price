from price.extension import api
from price.modules.price.endpoints import (
    PriceTest,
    PriceEntryPoint,
    PriceShop,
    PriceMenu,
)

api.add_resource(
    PriceTest,
    '/price_test'
)
api.add_resource(
    PriceEntryPoint,
    '/entry_point/<int:entry_point_id>'
)
api.add_resource(
    PriceShop,
    '/shop/<int:shop_id>'
)
api.add_resource(
    PriceMenu,
    '/price_menu'
)
