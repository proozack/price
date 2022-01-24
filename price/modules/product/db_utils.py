import datetime
from price import db
from sqlalchemy import and_, func
from price.utils.db_transaction import commit_after_execution

from price.modules.product.models import (
    ProductDefinition,
    ProductImg,
    ProductShop,
    ProductShopPrice,
    ProductCategoryDef,
    ProductCategory,
)

import logging
log = logging.getLogger(__name__)


class ProductCategoryDefDbu():
    def get_all_category(self):
        return db.session.query(
            ProductCategoryDef.id,
            ProductCategoryDef.name
        ).all()

    def get_category_by_id(self, cateory_def_id):
        return db.session.quer(
            ProductCategoryDef.id,
            ProductCategoryDef.name
        ).filter(
            and_(
                ProductCategoryDef.id == cateory_def_id,
                ProductCategoryDef.active.is_(True)
            )
        ).first()

    def get_category_by_name(self, name):
        return db.session.query(
            ProductCategoryDef.id,
            ProductCategoryDef.name
        ).filter(
            and_(
                ProductCategoryDef.name == name,
                ProductCategoryDef.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, category_def_id):
        result = self.get_category_by_id(category_def_id)
        if result:
            return result.id
        return None

    def add_category(self, name, meta_category_id):
        result = self.get_category_by_name(name)
        log.debug('Result for searching name: %r', result)
        if not result:
            log.debug('Save new category definition %r %r', name, meta_category_id)
            pcd = ProductCategoryDef(name, meta_category_id)
            db.session.add(pcd)
            db.session.flush()
            result = pcd.id
        else:
            log.debug('Save new meta_category_id: {} for category {}'.format(meta_category_id, name))
            pcd = ProductCategoryDef.query.filter(
                ProductCategoryDef.id == result.id
            ).first()
            pcd.name = name
            pcd.meta_category_id = meta_category_id
            pcd.last_update_date = datetime.datetime.now()
            pcd.last_update_by = 1
            db.session.flush()
            result = pcd
        return result

    @commit_after_execution
    def c_add_category(self, name, meta_category_id):
        return self.add_category(name, meta_category_id)


class ProductCategoryDbu():
    def _get_all(self):
        return db.session.query(
            ProductCategory.id,
            ProductCategory.product_definition_id,
            ProductCategory.product_category_id
        )

    def get_all(self):
        return self._get_all().all()

    def get_by_product_category_id(self, product_category_id):
        return self._get_all().filter(
            and_(
                ProductCategory.product_category_id == product_category_id,
                ProductCategory.active.is_(True)
            )
        ).all()

    def get_by_product_definition_id(self, product_definition_id):
        return self._get_all().filter(
            and_(
                ProductCategory.product_definition_id == product_definition_id,
                ProductCategory.active.is_(True)
            )
        ).all()

    def get_by_id(self, id):
        return self._get_all().filter(
            and_(
                ProductCategory.id == id,
                ProductCategory.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, product_definition_id, product_category_id):
        return self._get_all().filter(
            and_(
                ProductCategory.product_category_id == product_category_id,
                ProductCategory.product_definition_id == product_definition_id,
                ProductCategory.active.is_(True)
            )
        ).one_or_none()

    def add(self, product_definition_id, product_category_id):
        result = self.is_exists(product_definition_id, product_category_id)
        if not result:
            pc = ProductCategory(product_definition_id, product_category_id)
            db.session.add(pc)
            db.session.flush()
            result = pc
        else:
            pc = ProductCategory.query.filter(
                and_(
                    ProductCategory.product_category_id == product_category_id,
                    ProductCategory.product_definition_id == product_definition_id,
                    ProductCategory.active.is_(True)
                )
            )
            pc.product_definition_id = product_definition_id
            pc.product_category_id = product_category_id
            pc.last_update_by = 1
            pc.last_update_date = datetime.datetime.now()
            db.session.flush()
            result = pc
        return result

    @commit_after_execution
    def c_add(self, product_definition_id, product_category_id):
        return self.add(product_definition_id, product_category_id)


class ProductDefinitionDbu():
    def get_all(self):
        return db.session.query(
            ProductDefinition.id,
            ProductDefinition.name,
            ProductDefinition.ean,
            ProductDefinition.brand,
            ProductDefinition.collection,
        ).all()

    def get_by_name(self, name):
        return db.session.query(
            ProductDefinition.id,
            ProductDefinition.name,
            ProductDefinition.ean,
            ProductDefinition.brand,
            ProductDefinition.collection,
        ).filter(
            and_(
                ProductDefinition.name == name,
                ProductDefinition.active.id_(True)
            )
        ).all()

    def get_by_id(self, id):
        return db.session.query(
            ProductDefinition.id,
            ProductDefinition.name,
            ProductDefinition.ean,
            ProductDefinition.brand,
            ProductDefinition.collection,
        ).filter(
            and_(
                ProductDefinition.id == id,
                ProductDefinition.name.active.is_(True)
            )
        ).all()

    def is_exists(self, name, brand):
        return db.session.query(
            ProductDefinition.id
        ).filter(
            and_(
                ProductDefinition.name == name,
                ProductDefinition.brand == brand,
                ProductDefinition.active.is_(True)
            )
        ).one_or_none()

    def add(self, name, brand):
        result = self.is_exists(name, brand)
        if not result:
            pd = ProductDefinition(name, brand)
            db.session.add(pd)
            db.session.flush()
            result = pd
        else:
            pd = ProductDefinition.query.filter(
                and_(
                    ProductDefinition.name == name,
                    ProductDefinition.brand == brand
                )
            ).first()
            pd.name = name
            pd.brand = brand
            pd.last_update_by = datetime.datetime.now()
            pd.last_update_by = 1
            db.session.flush()
            result = pd
        return result

    @commit_after_execution
    def c_add(self, name, brand):
        return self.add(name, brand)


class ProductImgDbu():
    def _get_all(self):
        return db.session.query(
            ProductImg.id,
            ProductImg.product_definition_id,
            ProductImg.path_thumbs,
            ProductImg.img_source,
            ProductImg.orginal_images_id,
            ProductImg.path_big
        )

    def get_all(self):
        return self._get_all().all()

    def get_by_id(self, id):
        return self._get_all().filter(
            and_(
                ProductImg.id == id,
                ProductImg.active.is_(True)
            )
        ).one_or_none()

    def get_by_product_definition_id(self, product_definition_id):
        return self._get_all().filter(
            and_(
                ProductImg.product_definition_id == product_definition_id,
                ProductImg.active.is_(True)
            )
        ).all()

    def get_by_imp_catalog_page_id(self, imp_catalog_page_id):
        return self._get_all().filter(
                and_(
                    ProductImg.img_source == 'imp_product_page',
                    ProductImg.orginal_images_id == imp_catalog_page_id
                )
            ).all()

    def is_exists(self, product_definition_id, path_thumbs):
        return self._get_all().filter(
            and_(
                ProductImg.product_definition_id == product_definition_id,
                ProductImg.path_thumbs == path_thumbs,
                ProductImg.active.is_(True)
            )
        ).one_or_none()

    def add(self, product_definition_id, path_thumbs, img_source, orginal_images_id, path_big):
        result = self.is_exists(product_definition_id, path_thumbs)
        if not result:
            pi = ProductImg(product_definition_id, path_thumbs, img_source, orginal_images_id, path_big)
            db.session.add(pi)
            db.session.flush()
            result = pi
        else:
            pi = ProductImg.query.filter(
                and_(
                    ProductImg.product_definition_id == product_definition_id,
                    ProductImg.path_thumbs == path_thumbs,
                    ProductImg.active.is_(True)
                )
            )
            pi.product_definition_id = product_definition_id
            pi.path_thumbs = path_thumbs
            pi.img_source = img_source
            pi.orginal_images_id = orginal_images_id
            pi.last_update_by = 1
            pi.last_update_date = datetime.datetime.now()
            pi.path_big = path_big
            result = pi
            db.session.flush()
        return result


class ProductShopDbu():
    def _get_all(self):
        return db.session.query(
            ProductShop.id,
            ProductShop.product_definition_id,
            ProductShop.shop_id,
            ProductShop.product_url,
            ProductShop.imp_catalog_page_id
        )

    def get_by_id(self, id):
        return self._get_all().filter(
            and_(
                ProductShop.id == id,
                ProductShop.active.is_(True)
            )
        ).one_or_none()

    def get_by_product_definition_id(self, product_definition_id):
        return self._get_all().filter(
            and_(
                ProductShop.product_definition_id == product_definition_id,
                ProductShop.active.is_(True)
            )
        ).all()

    def get_by_imp_catalog_page_id(self, imp_catalog_page_id):
        return self._get_all().filter(
            and_(
                ProductShop.imp_catalog_page_id == imp_catalog_page_id,
                ProductShop.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, product_definition_id, imp_catalog_page_id):
        return self._get_all().filter(
            and_(
                ProductShop.product_definition_id == product_definition_id,
                ProductShop.imp_catalog_page_id == imp_catalog_page_id,
                ProductShop.active.is_(True)
            )
        ).one_or_none()

    def add(self, product_definition_id, shop_id, product_url, imp_catalog_page_id):
        result = self.is_exists(product_definition_id, imp_catalog_page_id)
        if not result:
            ps = ProductShop(product_definition_id, shop_id, product_url, imp_catalog_page_id)
            db.session.add(ps)
            db.session.flush()
            result = ps
        else:
            ps = ProductShop.query.filter(
                and_(
                    ProductShop.product_definition_id == product_definition_id,
                    ProductShop.imp_catalog_page_id == imp_catalog_page_id,
                    ProductShop.active.is_(True)
                )
            ).first()
            ps.product_definition_id = product_definition_id
            ps.shop_id = shop_id
            ps.product_url = product_url
            ps.imp_catalog_page_id = imp_catalog_page_id
            ps.last_update_date = datetime.datetime.now()
            ps.last_update_by = 1
            db.session.flush()
            result = ps
        return ps

    @commit_after_execution
    def c_add(self, product_definition_id, shop_id, product_url, imp_catalog_page_id):
        return self.add(product_definition_id, shop_id, product_url, imp_catalog_page_id)


class ProductShopPriceDbu():
    def _get_all(self):
        return db.session.query(
            ProductShopPrice.id,
            ProductShopPrice.product_shop_id,
            ProductShopPrice.scan_date,
            ProductShopPrice.price,
            ProductShopPrice.currency
        )

    def get_by_id(self, id):
        return self._get_all().filter(
            and_(
                ProductShopPrice.id == id,
                ProductShopPrice.active.is_(True)
            )
        ).one_or_none()

    def get_by_product_shop_id(self, product_shop_id):
        return self._get_all().filter(
            and_(
                ProductShopPrice.product_shop_id == product_shop_id,
                ProductShopPrice.active.is_(True)
            )
        ).all()

    def get_by_product_shop_id_for_date(self, product_shop_id, scan_date):
        return self._get_all().filter(
            and_(
                ProductShopPrice.product_shop_id == product_shop_id,
                ProductShopPrice.scan_date == scan_date,
                ProductShop.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, product_shop_id, scan_date):
        return self.get_by_product_shop_id_for_date(product_shop_id, scan_date)

    def add(self, product_shop_id, scan_date, price, currency):
        result = self.is_exists(product_shop_id, scan_date)
        if not result:
            psp = ProductShopPrice(product_shop_id, scan_date, price, currency)
            db.session.add(psp)
            db.session.flush()
            result = psp
        else:
            psp = ProductShopPrice.query.filter(
                and_(
                    ProductShopPrice.product_shop_id == product_shop_id,
                    ProductShopPrice.scan_date == scan_date,
                    ProductShop.active.is_(True)
                )
            )
            psp.product_shop_id = product_shop_id
            psp.scan_date = scan_date
            psp.price = price
            psp.currency = currency
            psp.last_update_by = 1
            psp.last_update_date = datetime.datetime.now()
            db.session.flush()
            result = psp
        return result

    @commit_after_execution
    def c_add(self, product_shop_id, scan_date, price, currency):
        return self.add(product_shop_id, scan_date, price, currency)


class CatalogPage():
    def _get_list_product_bq(self):
        img = db.session.query(
            ProductDefinition.name,
            ProductDefinition.brand,
            func.max(ProductImg.path_thumbs).label('path_thumbs')
        ).join(
            ProductDefinition,
            ProductDefinition.id == ProductImg.product_definition_id
        ).filter(
            ProductImg.img_source == 'imp_catalog_page'
        ).group_by(
            ProductDefinition.name,
            ProductDefinition.brand,
        ).cte('img')

        return db.session.query(
            ProductDefinition.name,
            ProductDefinition.brand,
            func.min(ProductShopPrice.price).label('min_price'),
            func.max(ProductShopPrice.price).label('max_price'),
            func.count(ProductShop.id).label('count_product'),
            img.c.path_thumbs
        ).join(
            ProductShop,
            ProductShop.product_definition_id == ProductDefinition.id
        ).join(
            ProductCategory,
            ProductCategory.product_definition_id == ProductDefinition.id
        ).join(
            ProductCategoryDef,
            ProductCategoryDef.id == ProductCategory.product_category_id
        ).join(
            ProductShopPrice,
            ProductShopPrice.product_shop_id == ProductShop.id
        ).join(
            img,
            and_(
                img.c.brand == ProductDefinition.brand,
                img.c.name == ProductDefinition.name
            ),
            isouter=True
        ).group_by(
            ProductDefinition.name,
            ProductDefinition.brand,
            img.c.path_thumbs
        )

    def get_list_product_by_meta_category_id(self, meta_category_id, scan_date):
        return self._get_list_product_bq().filter(
            and_(
                ProductCategoryDef.meta_category_id == meta_category_id,
                ProductShopPrice.scan_date == scan_date,
                ProductCategory.active.is_(True)
            )
        )

    def get_image_for_catalog(self, name, brand):
        return db.session.query(
            ProductDefinition.id,
            ProductImg.path_thumbs
        ).join(
            ProductDefinition,
            ProductDefinition.id == ProductImg.product_definition_id
        ).filter(
            and_(
                ProductDefinition.name == name,
                ProductDefinition.brand == brand
            )
        ).first()

    def get_product_view(self, brand, name, scan_date):
        log.debug('Search product for Brand: {} Name: {}'.format(brand, name))
        return db.session.query(
            ProductDefinition.id,
            ProductDefinition.name,
            ProductDefinition.brand,
            ProductShop.product_url,
            ProductShop.imp_catalog_page_id,
            ProductShop.id.label('product_shop_id'),
            ProductShop.shop_id,
            ProductShopPrice.price,
            ProductShopPrice.currency,
            ProductImg.path_thumbs
        ).join(
            ProductShop,
            ProductShop.product_definition_id == ProductDefinition.id
        ).join(
            ProductShopPrice,
            ProductShopPrice.product_shop_id == ProductShop.id
        ).join(
            ProductImg,
            and_(
                ProductDefinition.id == ProductImg.product_definition_id,
                ProductImg.img_source == 'imp_catalog_page',
                ProductImg.orginal_images_id == ProductShop.imp_catalog_page_id
            ),
            isouter=True
        ).filter(
            and_(
                ProductDefinition.brand == brand,
                ProductDefinition.name == str(name),
                ProductDefinition.active.is_(True),
                ProductShopPrice.scan_date == scan_date
            )
        ).group_by(
            ProductDefinition.id,
            ProductDefinition.name,
            ProductDefinition.brand,
            ProductShop.product_url,
            ProductShop.imp_catalog_page_id,
            ProductShop.id,
            ProductShop.shop_id,
            ProductShopPrice.price,
            ProductShopPrice.currency,
            ProductImg.path_thumbs
        ).order_by(
            ProductShopPrice.price.asc()
        ).all()

    def _get_product_category(self):
        return db.session.query(
            ProductShop.id.label('product_shop_id'),
            ProductShop.product_definition_id,
            ProductShop.imp_catalog_page_id,
            ProductCategory.product_category_id,
            ProductCategory.active,
            ProductCategoryDef.name.label('category_name')
        ).join(
            ProductCategory,
            ProductCategory.product_definition_id == ProductShop.product_definition_id
        ).join(
            ProductCategoryDef,
            ProductCategoryDef.id == ProductCategory.product_category_id
        )

    def get_product_category_by_product_shop_id(self, product_shop_id):
        return self._get_product_category().filter(
            ProductShop.id == product_shop_id
        ).all()

    def get_product_category_by_imp_catalog_page_id(self, imp_catalog_page_id):
        return self._get_product_category().filter(
            ProductShop.imp_catalog_page_id == imp_catalog_page_id
        ).all()
