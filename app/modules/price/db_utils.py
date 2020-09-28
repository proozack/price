from app import db
from sqlalchemy import and_
from app.modules.price.models import (EntryPoint, Shop, Category, Ofert, Brand)
from app.utils.url_utils import UrlUtils

import logging
log = logging.getLogger(__name__)


class EntryPointsDbUtils():

    def get_list_all_entry_points(self):
        ep = EntryPoint
        result = db.session.query(
            ep.id,
            ep.url
        ).filter(
            ep.active == True, # noqa E712
            ep.deleted == False # noqa E712
        )
        return [
            entity
            for entity in result
        ]

    def is_entry_point_exists(self, url):
        return db.session.query(
            EntryPoint.id
        ).filter(
            EntryPoint.url == url
        ).first()

    def add_enty_point_with_check_shop(self, entry_point, category_id):
        entry_point_id = self.is_entry_point_exists(entry_point)
        if not entry_point_id:
            u = UrlUtils(entry_point)
            sdu = ShopDbUtils()
            shop_id = sdu.add_new_shop(u.domain)
            ep = EntryPoint(entry_point, category_id, shop_id)
            log.info('Added new entry point %r for catgeory_id: %r,  shop_id: %r', entry_point,  category_id, shop_id)
            db.session.add(ep)
            db.session.commit()
        else:
            log.info('Entry point %r exist', entry_point)

    def add_list_enty_points_with_check_shop(self, list_entry_point, category_id):
        for entry_point in list_entry_point:
            self.add_enty_point_with_check_shop(entry_point, category_id)


class ShopDbUtils():
    def is_shop_exists(self, url: str):
        return db.session.query(
            Shop.id
        ).filter(
            Shop.url == url
        ).first()

    def add_new_shop(self, url) -> None:
        log.info('Add new shop domain %r', url)
        id_shop = self.is_shop_exists(url)
        if not id_shop:
            s = Shop(url)
            db.session.add(s)
            db.session.commit()
            log.info('save object s: %r', s.id)
            return s.id
        else:
            return id_shop


class OfertDbUtils():
    def get_all_ofert_by_category(self, category_id: int) -> list:
        return db.session.query(
            Ofert.id,
            Ofert.title,
            Ofert.entry_point_id,
            Category.name,
            Ofert.manufacturer
        ).join(
            EntryPoint,
            EntryPoint.id == Ofert.entry_point_id
        ).join(
            Category,
            Category.id == EntryPoint.category_id
        ).all()

    def get_all_brand_by_category(self, category_id: int) -> list:
        result = db.session.query(
            Ofert.manufacturer
        ).filter(
            and_(
                Ofert.manufacturer.isnot(None),
                Ofert.manufacturer != ''
            )
        ).group_by(
            Ofert.manufacturer
        ).all()
        return [
            ent[0].lower()
            for ent in result
        ]


class BrandDbUtils():
    def add_brand(self, brand_name, logo=None):
        b = Brand(brand_name, logo)
        db.session.add(b)
        db.session.commit()

    def get_all_brand(self):
        return db.session.query(
            Brand.id,
            Brand.name
        ).all()

    def get_all_brand_as_list(self):
        return [
            brands_tuple[1]
            for brands_tuple in self.get_all_brand()
        ]

    def is_brand_exists(self, name):
        return db.session.query(
            Brand.id
        ).filter(
            Brand.name == name
        ).first()
