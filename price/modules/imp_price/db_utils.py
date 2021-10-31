import datetime
from price import db
from sqlalchemy import and_
from price.utils.db_transaction import commit_after_execution
from price.modules.price.models import EntryPoint 
from price.modules.imp_price.models import (ImpCatalogPage, ImpProductPage, ImpProductPrice)
from price.modules.imp_price.local_types import ProductPage


import logging
log = logging.getLogger(__name__)


class ImpCatalogPageDbU():
    
    def is_exists(self, url):
        return db.session.query(
            ImpCatalogPage.id
        ).filter(
            and_(
                ImpCatalogPage.url == url,
                ImpCatalogPage.active == True,
                ImpCatalogPage.deleted != True
            )
        ).first()

    def add_catalog_page(self, entry_point_id, url, title, img, brand):
        catalog_page_id = self.is_exists(url)
        if not catalog_page_id:
            log.debug('Add new record: EpID="%s", url="%s" title="%s"', entry_point_id, url, title)
            imp = ImpCatalogPage(entry_point_id, url, title, img, brand)
            db.session.add(imp)
            db.session.flush()
            catalog_page_id = imp.id
        return catalog_page_id

    @commit_after_execution
    def c_add_catalog_page(self, entry_point_id, url, title, img, brand):
        return self.add_catalog_page(entry_point_id, url, title, img, brand)

    def get_product(self, scan_date):
        return db.session.query(
            ImpCatalogPage.entry_point_id,
            ImpCatalogPage.title,
            ImpCatalogPage.brand,
            ImpCatalogPage.url,
            ImpCatalogPage.img,
            ImpProductPrice.price,
            ImpProductPrice.currency
        ).join(
            ImpProductPrice,
            ImpProductPrice.imp_catalog_page_id == ImpCatalogPage.id
        ).filter(
            ImpProductPrice.scan_date == scan_date
        ).all()

    @commit_after_execution
    def deactivate_product(self, catalog_page_id):
        result = self.get_catalog_page(catalog_page_id)
        result.active = False
        result.last_update_date = datetime.datetime.now()
        db.session.flush()

    def get_not_processing_url(self, url_str):
        query = db.session.query(
            ImpCatalogPage.id,
            ImpCatalogPage.url
        ).join(
            ImpProductPage,
            ImpProductPage.imp_catalog_page_id == ImpCatalogPage.id,
            isouter = True
        ).filter(
            and_(
                ImpCatalogPage.active == True,
                ImpProductPage.id.is_(None)
            )
        )
        if url_str:
            search_str = '%{}%'.format(url_str)
            query = query.filter(ImpCatalogPage.url.like(search_str))
        return query.all()

    def get_url_by_shop_id(self, shop_id):
        return db.session.query(
            ImpCatalogPage.id,
            ImpCatalogPage.url
        ).join(
            EntryPoint,
            EntryPoint.id == ImpCatalogPage.entry_point_id
        ).filter(
            and_(
                EntryPoint.shop_id == shop_id,
                ImpCatalogPage.active == True
                )
        ).all()

    def get_catalog_page(self, catalog_page_id):
        return db.session.query(
            ImpCatalogPage
        ).filter(
            ImpCatalogPage.id == catalog_page_id
        ).one_or_none()


class ImpProductPageDbU():

    @commit_after_execution
    def c_save_product_page(self, pp: ProductPage) -> int:
        product_page_id = self.is_exists(pp.imp_catalog_page_id)
        if product_page_id:
            return self.update_product_page(product_page_id, pp)
        else:
            return self.add_product_page(pp)

    def add_product_page(self, pp: ProductPage) -> int:
        ipp = ImpProductPage()
        local_dict = pp.get_dict()
        for field in pp.get_dict():
            value = local_dict.get(field) if local_dict.get(field) != NotImplemented else None
            setattr(ipp, field, value)
        db.session.add(ipp)
        db.session.flush()
        return ipp.id

    def update_product_page(self, product_page_id,  pp):
        result = self.get_product_page_by_id(product_page_id)
        if pp.deleted:
            result.deleted = pp.deleted
        else:
            local_dict = pp.get_dict()
            for field in pp.get_dict():
                # setattr(result, field, local_dict.get(field))
                value = local_dict.get(field) if local_dict.get(field) != NotImplemented else None
                setattr(result, field, value)
            result.last_update_date = datetime.datetime.now()
        db.session.flush()

    def is_exists(self, imp_catalog_page_id):
        return db.session.query(
            ImpProductPage.id
        ).filter(
            ImpProductPage.imp_catalog_page_id == imp_catalog_page_id,
        ).one_or_none()


    def get_product_page_by_id(self, product_page_id):
        return db.session.query(
            ImpProductPage
        ).filter(
            ImpProductPage.id == product_page_id
        ).with_for_update()
        # .first()

class ImpProductPriceDbU():
    
    def add_product_price(self, imp_catalog_page_id, price, currency, scan_date):
        product_price_id = self.is_exists(imp_catalog_page_id, price, scan_date)
        if not  product_price_id:
            imp = ImpProductPrice(imp_catalog_page_id, price, currency, scan_date)
            db.session.add(imp)
            db.session.flush()
            product_price_id = imp.id
        return product_price_id 

    @commit_after_execution
    def c_add_product_price(self, imp_catalog_page_id, price, currency, scan_date):
        return self.add_product_price(imp_catalog_page_id, price, currency, scan_date)

    def is_exists(self, imp_catalog_page_id, price, scan_date):
        return db.session.query(
            ImpProductPrice.id
        ).filter(
            and_(
                ImpProductPrice.imp_catalog_page_id == imp_catalog_page_id,
                ImpProductPrice.price == price,
                ImpProductPrice.scan_date == scan_date,
                ImpProductPrice.active == True,
                ImpProductPrice.deleted != True
            )
        ).first()

