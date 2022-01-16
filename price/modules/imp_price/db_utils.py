import datetime
from sqlalchemy.sql.expression import func
from sqlalchemy import cast
from price import db
import sqlalchemy
from sqlalchemy import and_, or_
from sqlalchemy import Date
from price.utils.db_transaction import commit_after_execution
from price.modules.price.models import EntryPoint
from price.modules.imp_price.models import (
    ImpCatalogPage,
    ImpProductPage,
    ImpProductPrice,
    ImpCatalogPageStatus
)
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
                ImpCatalogPage.active.is_(True),
                ImpCatalogPage.deleted.isnot(True)
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

    def get_product_by_id(self, imp_catalog_page_id, scan_date):
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
            and_(
                ImpCatalogPage.id == imp_catalog_page_id,
                ImpProductPrice.scan_date == scan_date,
                ImpCatalogPage.active.is_(True)
            )
        ).one_or_none()

    @commit_after_execution
    def deactivate_product(self, catalog_page_id):
        result = self.get_catalog_page(catalog_page_id)
        result.active = False
        result.last_update_date = datetime.datetime.now()
        db.session.flush()

    def get_not_processing_url(self, url_str=None, entry_point_id=None):
        query = db.session.query(
            ImpCatalogPage.id,
            ImpCatalogPage.url
        ).join(
            ImpProductPage,
            ImpProductPage.imp_catalog_page_id == ImpCatalogPage.id,
            isouter=True
        ).filter(
            and_(
                ImpCatalogPage.active.is_(True),
                ImpProductPage.id.is_(None)
            )
        )
        if url_str:
            search_str = '%{}%'.format(url_str)
            query = query.filter(ImpCatalogPage.url.like(search_str))

        if entry_point_id:
            query = query.filter(ImpCatalogPage.entry_point_id == entry_point_id)

        return query.all()

    def get_processed_entry_points(self):
        return db.session.query(
            ImpCatalogPage.entry_point_id
        ).join(
            ImpProductPage,
            ImpProductPage.imp_catalog_page_id == ImpCatalogPage.id,
            isouter=True
        ).filter(
            ImpProductPage.id.isnot(None)
        ).group_by(
            ImpCatalogPage.entry_point_id
        ).all()

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
                ImpCatalogPage.active.is_(True)
                )
        ).all()

    def get_catalog_page(self, catalog_page_id):
        return db.session.query(
            ImpCatalogPage
        ).filter(
            ImpCatalogPage.id == catalog_page_id
        ).one_or_none()

    def get_tagging_product(self, imp_catalog_page_id):
        return db.session.query(
            ImpCatalogPage.id.label('imp_catalog_page_id'),
            ImpCatalogPage.brand.label('catalog_brand'),
            ImpCatalogPage.url.label('catalog_url'),
            ImpCatalogPage.title.label('catalog_title'),
            ImpCatalogPage.img.label('catalog_img'),
            ImpProductPage.brand.label('product_brand'),
            ImpProductPage.title.label('product_title'),
            ImpProductPage.category.label('product_category'),
            ImpProductPage.description.label('product_desc'),
            ImpProductPage.attributes['product_path'].label('product_path'),
        ).join(
            ImpProductPage,
            ImpCatalogPage.id == ImpProductPage.imp_catalog_page_id,
            isouter=True
        ).filter(
            and_(
                ImpCatalogPage.id == imp_catalog_page_id,
                ImpCatalogPage.active.is_(True)
            )
        ).one_or_none()

    def search_product_by_category(self, value):
        ilike_value = '%{}%'.format(value)
        return db.session.query(
            ImpCatalogPage.id.label('imp_catalog_page_id')
        ).join(
            ImpProductPage,
            ImpCatalogPage.id == ImpProductPage.imp_catalog_page_id,
            isouter=True
        ).filter(
            or_(
                func.lower(ImpCatalogPage.brand).ilike(ilike_value),
                func.lower(ImpCatalogPage.url).ilike(ilike_value),
                func.lower(ImpCatalogPage.title).ilike(ilike_value),
                func.lower(ImpCatalogPage.img).ilike(ilike_value),
                func.lower(ImpProductPage.brand).ilike(ilike_value),
                func.lower(ImpProductPage.title).ilike(ilike_value),
                func.lower(ImpProductPage.category).ilike(ilike_value),
                func.lower(ImpProductPage.description).ilike(ilike_value),
                cast(ImpProductPage.attributes, sqlalchemy.String).ilike(ilike_value)
            )
        ).all()

    def get_imp_catalog_page(self, imp_catalog_page_id=None, creation_date=None):
        pages = db.session.query(
            ImpCatalogPage.id.label('imp_catalog_page_id'),
            ImpCatalogPage.title.label('title')
        )
        if imp_catalog_page_id:
            pages = pages.filter(ImpCatalogPage.id == imp_catalog_page_id)
        if creation_date:
            pages = pages.filter((ImpCatalogPage.creation_date).cast(Date) == creation_date)
        return pages.all()

    def get_unprocessed_pages(self, scan_date=None):
        pages = db.session.query(
            ImpCatalogPage.id.label('imp_catalog_page_id')
        ).join(
            ImpCatalogPageStatus,
            ImpCatalogPageStatus.imp_catalog_page_id == ImpCatalogPage.id,
            isouter=True
        ).filter(
            and_(
                ImpCatalogPageStatus.id.is_(None),
                ImpCatalogPage.active.is_(True),
            )
        )
        if scan_date:
            pages = pages.filter(
                (ImpCatalogPage.creation_date).cast(Date) == scan_date
            )
            # (ImpCatalogPage.creation_date).cast(Date) == func.current_date()
        return pages.all()

    def _get_catalog_page_id(self):
        return db.session.query(
            ImpCatalogPage.id,
            ImpProductPrice.scan_date
        ).join(
            ImpProductPrice,
            ImpCatalogPage.id == ImpProductPrice.imp_catalog_page_id
        ).filter(
            ImpCatalogPage.active.is_(True)
        )

    def get_all_price_for_catalog_page(self):
        return self._get_catalog_page_id().all()


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

    def get_images_by_imp_catalog_page_id(self, imp_catalog_page_id):
        return db.session.query(
            ImpProductPage.images
        ).filter(
            and_(
                ImpProductPage.imp_catalog_page_id == imp_catalog_page_id,
                ImpProductPage.active.is_(True)
            )
        ).one_or_none()

    def get_product_info(self, imp_catalog_page_id):
        return db.session.query(
            ImpProductPage.imp_catalog_page_id,
            ImpProductPage.title,
            ImpProductPage.description,
            ImpProductPage.size,
            ImpProductPage.composition,
            ImpProductPage.color
        ).filter(
            ImpProductPage.imp_catalog_page_id == imp_catalog_page_id
        ).one_or_none()


class ImpProductPriceDbU():

    def add_product_price(self, imp_catalog_page_id, price, currency, scan_date):
        product_price_id = self.is_exists(imp_catalog_page_id, price, scan_date)
        if not product_price_id:
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
                ImpProductPrice.active.is_(True),
                ImpProductPrice.deleted.isnot(True)
            )
        ).first()


class ImpCatalogPageStatusDbU():
    def is_exists(self, imp_catalog_page_id):
        return db.session.query(
            ImpCatalogPageStatus.id,
            ImpCatalogPageStatus.specific_brand_date,
            ImpCatalogPageStatus.specific_category_date
        ).filter(
            and_(
                ImpCatalogPageStatus.imp_catalog_page_id == imp_catalog_page_id,
                ImpCatalogPageStatus.active.is_(True),
                ImpCatalogPageStatus.deleted.isnot(True)
            )
        ).first()

    def is_specific_brand(self, imp_catalog_page_id):
        return db.session.query(
            ImpCatalogPageStatus.specific_brand_date
        ).filter(
            and_(
                ImpCatalogPageStatus.imp_catalog_page_id == imp_catalog_page_id,
                ImpCatalogPageStatus.active.is_(True),
                ImpCatalogPageStatus.deleted.isnot(True)
            )
        ).first()

    def is_specific_category(self, imp_catalog_page_id):
        return db.session.query(
            ImpCatalogPageStatus.specific_category_date
        ).filter(
            and_(
                ImpCatalogPageStatus.imp_catalog_page_id == imp_catalog_page_id,
                ImpCatalogPageStatus.active.is_(True),
                ImpCatalogPageStatus.deleted.isnot(True)
            )
        ).first()

    def set_specific_category(self, imp_catalog_page_id):
        imp_catalog_page_status = self.is_exists(imp_catalog_page_id)
        new_date = datetime.datetime.now()
        if not imp_catalog_page_status:
            icps = ImpCatalogPageStatus(imp_catalog_page_id)
            icps.specific_category_date = new_date
            db.session.add(icps)
            imp_catalog_page_status = icps
        else:
            log.info('Change specific category date for ICP.ID {} old: {} -> new: {}'.format(
                imp_catalog_page_id,
                imp_catalog_page_status.specific_category_date,
                new_date
            ))
            icps = ImpCatalogPageStatus.query.filter(
                ImpCatalogPageStatus.id == imp_catalog_page_status.id
            ).first()
            icps.specific_category_date = new_date
        db.session.flush()
        return imp_catalog_page_status.id

    @commit_after_execution
    def c_set_specific_category(self, imp_catalog_page_id):
        return self.set_specific_category(imp_catalog_page_id)

    def set_specific_brand(self, imp_catalog_page_id):
        imp_catalog_page_status = self.is_exists(imp_catalog_page_id)
        new_date = datetime.datetime.now()
        if not imp_catalog_page_status:
            icps = ImpCatalogPageStatus(imp_catalog_page_id)
            icps.specific_brand_date = new_date
            db.session.add(icps)
            imp_catalog_page_status = icps
        else:
            log.info('Change specific category date for ICP.ID {} old: {} -> new: {}'.format(
                imp_catalog_page_id,
                imp_catalog_page_status.specific_category_date,
                new_date
            ))
            icps = ImpCatalogPageStatus.query.filter(
                ImpCatalogPageStatus.id == imp_catalog_page_status.id
            ).first()
            icps.specific_brand_date = new_date
        db.session.flush()
        return imp_catalog_page_status.id

    @commit_after_execution
    def c_set_specific_brand(self, imp_catalog_page_id):
        return self.set_specific_brand(imp_catalog_page_id)
