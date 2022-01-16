from price.extension import api
from price.modules.imp_price.endpoints import (
    ImpPriceTest,
    ImpCatalogPageStatus,
    ImpCatalogPageSearch,
    ImpCatalogProduct,
    ImpProductImagses,
    ImpProductInfo
)


api.add_resource(
    ImpPriceTest,
    '/imp_price_test'
)
api.add_resource(
    ImpCatalogPageStatus,
    '/catalog_page_status'
)
api.add_resource(
    ImpCatalogPageSearch,
    '/catalog_page_search/<string:field>/<string:value>'
)
api.add_resource(
    ImpCatalogProduct,
    '/catalog_product/<int:imp_catalog_page_id>/<string:scan_date>'
)
api.add_resource(
    ImpProductInfo,
    '/catalog_product/<int:imp_catalog_page_id>'
)
api.add_resource(
    ImpProductImagses,
    '/catalog_imagse/<int:imp_catalog_page_id>'
)
#   /<string:status_type>/<int:imp_catalog_page_id>'
