from price.extension import api
from price.modules.product.endpoints import (
    ProductTest,
    ProductDef,
    ProductCatalog,
    ProductCatalogImg,
    ProductViews,
    Start,
    ProductCategory,
    ProductCategoryAlt,
    ProductDefinition,
    ProductImg,
    ProductShopPrice,
    ProductRepair
)

api.add_resource(Start, '/')
api.add_resource(ProductTest, '/product_test')
api.add_resource(ProductDef, '/product_def')
api.add_resource(ProductCatalog, '/list_product/<string:category>/<int:page_id>')
api.add_resource(ProductCatalogImg, '/product_catalog_img/<string:name>/<string:brand>')
api.add_resource(ProductViews, '/product_views/<string:brand>/<string:name>')
api.add_resource(ProductCategory, '/product_category/<int:product_shop_id>')
api.add_resource(ProductCategoryAlt, '/product_category_alt/<int:imp_catalog_page_id>')
api.add_resource(ProductDefinition, '/product_definition/<int:imp_catalog_page_id>')
api.add_resource(ProductImg, '/product_images/<int:imp_catalog_page_id>')
api.add_resource(ProductShopPrice, '/product_shop_price/<int:imp_catalog_page_id>')
api.add_resource(ProductRepair, '/product_repair/<int:imp_catalog_page_id>')
