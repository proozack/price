from price import db
from price.modules.product.db_utils import (
    # ProductCategoryDbu
    ProductCategoryDefDbu,
    ProductDefinitionDbu,
    ProductShopDbu,
    ProductImgDbu,
    ProductShopPriceDbu,
    ProductCategoryDbu,
    CatalogPage
)
from price.modules.product.local_types import ProductObj
from price.utils.db_transaction import commit_after_execution
from price.utils.rest_util import get

import logging
log = logging.getLogger(__name__)


class Services():
    def list_category(self):
        pcd = ProductCategoryDefDbu()
        return pcd.get_all_category()

    def add_categroy(self, name, meta_category_id):
        log.debug('Try add category definition name: {} meta_category_id: {}'.format(name, meta_category_id))
        pcd = ProductCategoryDefDbu()
        pcd.c_add_category(name, meta_category_id)

    def list_product_def(self):
        pd = ProductDefinitionDbu()
        return pd.get_all()

    def add_product_def(self, name, brand):
        pd = ProductDefinitionDbu()
        return pd.add(name, brand)

    def add_product_shop(self, product_definition_id, shop_id, product_url, imp_catalog_page_id):
        ps = ProductShopDbu()
        return ps.add(product_definition_id, shop_id, product_url, imp_catalog_page_id)

    def add_product_img(self, product_definition_id, path_thumbs, img_source, orginal_images_id, path_big):
        pi = ProductImgDbu()
        return pi.add(product_definition_id, path_thumbs, img_source, orginal_images_id, path_big)

    def add_product_price(self, product_definition_id, scan_date, price, currency):
        psp = ProductShopPriceDbu()
        return psp.add(product_definition_id, scan_date, price, currency)

    def add_category(self, product_definition_id, product_category_id):
        pc = ProductCategoryDbu()
        pc.add(product_definition_id, product_category_id)

    @commit_after_execution
    def add_product(self, imp_catalog_page_id, scan_date):
        ps = ProductShopDbu()
        product_shop = ps.get_by_imp_catalog_page_id(imp_catalog_page_id)
        log.debug('Product shop: %r', product_shop)
        if product_shop:
            p = ProductObj(imp_catalog_page_id, scan_date)
            p.get_product_info()
            psp = ProductShopPriceDbu()
            psp.add(product_shop.id, scan_date, p.price, p.currency)
            log.debug('Save only new price for IMP.ID {}, ProductShopID: {}'.format(imp_catalog_page_id, product_shop.id)) # noqa E501

            p.load_data()
            product_def = self.save_product(p)
            log.debug('Save new ProductDef {}'.format(product_def))
        else:
            p = ProductObj(imp_catalog_page_id, scan_date)
            p.load_data()
            product_def = self.save_product(p)
            log.debug('Save new ProductDef {}'.format(product_def))

    def save_product(self, product_obj):
        product_def = self.add_product_def(product_obj.name, product_obj.brand)
        product_shop = self.add_product_shop(
            product_def.id,
            product_obj.shop_id,
            product_obj.product_url,
            product_obj.imp_catalog_page_id
        )
        for image in product_obj.images:
            product_img = self.add_product_img( # noqa F841
                product_def.id,
                image.get('path_thumbs'),
                image.get('img_source'),
                image.get('orginal_images_id'),
                image.get('path_big')
            )
        product_price = self.add_product_price( # noqa F841
            product_shop.id,
            product_obj.scan_date,
            product_obj.price,
            product_obj.currency
        )
        pcd = ProductCategoryDefDbu()
        #
        # To poniżej jest sensu
        #
        for category in product_obj.category:
            product_category = pcd.get_category_by_name(category)
            if not product_category:
                db.session.rollback()
                raise KeyError('No found catgeory: {}'.format(category))
            else:
                self.add_category(product_def.id, product_category.id)
        return product_def

    def get_list_product_by_meta_category_id(self, meta_category_id, scan_date):
        cp = CatalogPage()
        return cp.get_list_product_by_meta_category_id(meta_category_id, scan_date)

    def get_image_for_catalog(self, name, brand):
        cp = CatalogPage()
        return cp.get_image_for_catalog(name, brand)

    def get_category_for_view_by_product_shop_id(self, product_shop_id):
        cp = CatalogPage()
        return cp.get_product_category_by_product_shop_id(product_shop_id)

    def get_category_for_view_by_imp_catalog_page_id(self, imp_catalog_page_id):
        cp = CatalogPage()
        return cp.get_product_category_by_imp_catalog_page_id(imp_catalog_page_id)

    def get_product_for_view(self, brand, name, scan_date):
        cp = CatalogPage()
        pi = ProductImgDbu()
        result_list = []
        catalog_page_id_lst = []
        product_dsc = []
        product_img = []
        for ent in cp.get_product_view(brand, name, scan_date):
            product_info = get('http://127.0.0.1:7001/catalog_product/{}'.format(ent.imp_catalog_page_id))

            if not product_info:
                product_info = get('http://127.0.0.1:7001/catalog_product/{}/{}'.format(ent.imp_catalog_page_id, scan_date)) # noqa E501
            else:
                product_dsc.append(product_info.get('description'))

            product_category = get('http://127.0.0.1:7001/product_category/{}'.format(ent.product_shop_id))

            line = {
                'id': ent.id,
                'name': ent.name,
                'brand': ent.brand,
                'product_url': ent.product_url,
                'shop_id': ent.shop_id,
                'product_shop_id': ent.product_shop_id,
                'imp_catalog_page_id': ent.imp_catalog_page_id,
                'shop_name': get('http://127.0.0.1:7001/shop/{}'.format(ent.shop_id)).get('name'),
                'product_title': product_info.get('title'), # noqa E501
                'price': ent.price,
                'currency': ent.currency,
                'path_thumbs': ent.path_thumbs,
                'category': product_category,
            }
            catalog_page_id_lst.append(ent.imp_catalog_page_id)
            result_list.append(line)
            for images in pi.get_by_imp_catalog_page_id(ent.imp_catalog_page_id):
                product_img.append(images)
        return {
            'result_list': result_list,
            'product_dsc': product_dsc,
            'product_img': product_img,
        }

    def get_product_info(self, imp_catalog_page_id):
        pddbu = ProductDefinitionDbu()
        result = pddbu.get_product_info(imp_catalog_page_id)
        return result

    def get_product_images(self, imp_catalog_page_id):
        pidbu = ProductImgDbu()
        return pidbu.get_by_imp_catalog_page_id(imp_catalog_page_id)

    def get_product_price(self, imp_catalog_page_id):
        pspdbu = ProductShopPriceDbu()
        return pspdbu.get_by_imp_catalog_page_id(imp_catalog_page_id)
