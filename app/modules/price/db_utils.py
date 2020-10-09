from app import db
from sqlalchemy import and_
from app.modules.price.models import (EntryPoint, Shop, Category, Ofert, Brand, Product, KeyWord, KeyWordLink, MetaCategory, Image, ProductPrice, TagWordLink) # noqa E501
from app.utils.url_utils import UrlUtils
from app.utils.local_type import TempProduct
from app.utils.db_transaction import commit_after_execution
# from app.utils.db_transaction import commit_section

import logging
log = logging.getLogger(__name__)


class EntryPointsDbUtils():
    def get_list_all_entry_points(self, enty_point_id=None):
        ep = EntryPoint
        if enty_point_id:
            result = db.session.query(
                ep.id,
                ep.url
            ).filter(
                and_(
                    ep.active == True, # noqa E712
                    ep.deleted == False, # noqa E712
                    ep.id == enty_point_id
                )
            )
        else:
            result = db.session.query(
                ep.id,
                ep.url
            ).filter(
                and_(
                    ep.active == True, # noqa E712
                    ep.deleted == False # noqa E712
                )
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

    def add_entry_point_with_check_shop(self, entry_point, category_id):
        entry_point_id = self.is_entry_point_exists(entry_point)
        if not entry_point_id:
            u = UrlUtils(entry_point)
            sdu = ShopDbUtils()
            shop_id = sdu.add_new_shop(u.domain)
            ep = EntryPoint(entry_point, category_id, shop_id)
            log.info('Added new entry point %r for category_id: %r,  shop_id: %r', entry_point,  category_id, shop_id)
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

    def get_all_oferts(self, ofert_id=None, shop_id=None):
        o = db.session.query(
            Ofert.id,
            Ofert.title,
            Ofert.url,
            Ofert.image,
            Ofert.price,
            Ofert.currency,
            Ofert.manufacturer,
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            Shop.id.label('shop_id'),
            Shop.url.label('shop_url'),
            Image.control_sum,
            Ofert.creation_date.label('product_date'),
            Image.dimension,
            Image.size,
            Image.orientation,
            Image.main_color
        ).join(
            EntryPoint,
            EntryPoint.id == Ofert.entry_point_id
        ).join(
            Category,
            Category.id == EntryPoint.category_id
        ).join(
            Shop,
            Shop.id == EntryPoint.shop_id
        ).join(
            Image,
            Image.image == Ofert.image
        )
        if ofert_id:
            o = o.filter(Ofert.id == ofert_id)
        if shop_id:
            o = o.filter(Shop.id == shop_id)
        return o.all()


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

    def get_brand_id_by_name(self, name):
        """Synonym for method is_brand_exists"""
        return self.is_brand_exists(name)


class ProductDbUtils():
    """
    def add_product(self, name, brand_id, category_id):
        p = Product(name, brand_id, category_id)
        db.session.add(p)
        db.session.commit()
    """

    def if_product_exists(self, name, brand_id, category_id):
        return db.session.query(
            Product.id
        ).filter(
            Product.name == name,
            Product.brand_id == brand_id,
            Product.category_id == category_id,
            Product.active == True, # noqa E712
            Product.deleted == False
        ).first()

    @commit_after_execution
    def add_product(self, tp: TempProduct): # noqa F811
        bdbu = BrandDbUtils()
        ppdbu = ProductPriceDbUtils()

        brand_id = bdbu.get_brand_id_by_name(tp.manufacturer)
        log.info('Tp object %r', tp.get_dict())
        log.info('Brand ID %r', brand_id)
        product_found = self.if_product_exists(tp.title, brand_id, tp.category_id)
        if not product_found:
            p = Product(tp.title, brand_id, tp.category_id, tp.slug)
            db.session.add(p)
            db.session.flush()
            product_found = p.id
        else:
            log.warning('Product exists %r on ID = %r', tp.title, product_found.id)

        ppdbu.add_price_to_product(product_found, tp.shop_id, tp.price, tp.product_date)


class ProductPriceDbUtils():
    def add_price_to_product(self, product_id, shop_id, price, date_price):
        pp = ProductPrice(product_id, shop_id, price, date_price)
        db.session.add(pp)
        db.session.flush()


class KeyWordDbUtils():
    def add_word(self, word):
        k = KeyWord(word)
        db.session.add(k)
        db.session.flush()
        return k.id

    def if_word_exists(self, word):
        return db.session.query(
            KeyWord.id
        ).filter(
            KeyWord.value == word
        ).first()


class KeyWordLinkDbUtils():
    def add_word_to_category(self, category_id, word):
        kwdu = KeyWordDbUtils()
        key_word_id = kwdu.if_word_exists(word)
        if not key_word_id:
            key_word_id = kwdu.add_word(word)
        kwl = KeyWordLink(category_id, key_word_id)
        db.session.add(kwl)
        db.session.commit()

    def get_all_word(self):
        return db.session.query(
            KeyWord.value,
            KeyWordLink.category_id,
            KeyWord.id
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id
        ).all()

    def get_word_by_category(self, category_id):
        words = db.session.query(
            KeyWord.value
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id
        ).filter(
            KeyWordLink.category_id == category_id
        ).all()
        return [
            word[0]
            for word in words
        ]


class CategoryDbUtils():
    def add_category(self, name, meta_category_id):
        catgeory = Category(name, meta_category_id)
        db.session.add(catgeory)
        db.session.commit()
        return catgeory.id

    def get_all_category(self):
        return db.session.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            MetaCategory.id.label('metacategory_id'),
            MetaCategory.name.label('meta_category_name')
        ).join(
            MetaCategory,
            MetaCategory.id == Category.meta_category_id
        ).all()

    def get_category_name_by_id(self, category_id):
        catgeory = db.session.query(
            Category.name
        ).filter(
            Category.id == category_id
        ).first()
        return catgeory[0]


class TagWordLinkDbUtils():

    @commit_after_execution
    def add_tag(self, name, product_id):
        kwdu = KeyWordDbUtils()
        result = kwdu.if_word_exists(name)
        if result:
            word_id = result
        else:
            word_id = kwdu.add_word(name)
        twl = TagWordLink(product_id, word_id)
        db.session.add(twl)

    def get_tags(self):
        tags = db.session.query(
            KeyWord.value
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id,
            isouter=True
        ).filter(
            KeyWordLink.id.is_(None)
        ).all()
        return [
            tag[0]
            for tag in tags
        ]
