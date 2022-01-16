from price.extension import api
from price.modules.product.endpoints import (
    ProductTest,
    ProductDef,
    ProductCatalog,
    ProductCatalogImg,
    ProductViews,
    Start
)

api.add_resource(Start, '/')
api.add_resource(ProductTest, '/product_test')
api.add_resource(ProductDef, '/product_def')
api.add_resource(ProductCatalog, '/list_product/<string:category>/<int:page_id>')
api.add_resource(ProductCatalogImg, '/product_catalog_img/<string:name>/<string:brand>')
api.add_resource(ProductViews, '/product_views/<string:brand>/<string:name>')
