from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String, Numeric, Date
from sqlalchemy import Sequence
from app.utils.models import DbUtils
from app import db


import logging
log = logging.getLogger(__name__)


class Ofert(DbUtils):
    __tablename__ = 'price_ofert'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    entry_point_id = Column(
        Integer,
        ForeignKey("price_entry_point.id"),
        nullable=False,
        comment='FK to entry_point_id table'
    )
    title = Column(Text)
    price = Column(Float)
    currency = Column(String)
    url = Column(Text)
    image = Column(Text)
    manufacturer = Column(Text)

    def __init__(self, ntuple_ofert, entry_point_id):
        result = dict(ntuple_ofert._asdict())
        self.title = result.get('title')
        self.price = result.get('price')
        self.currency = result.get('currency')
        self.url = result.get('url')
        self.image = result.get('image')
        self.entry_point_id = entry_point_id
        self.manufacturer = result.get('manufacturer')

    def __repr__(self):
        return '<Ofert> title: {} ({} {})'.format(self.title, self.price, self.currency)


class Image(DbUtils):
    __tablename__ = 'price_image'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    control_sum = Column(Text)
    image = Column(Text)
    dimension = Column(Text)
    size = Column(Integer)
    orientation = Column(Text)
    main_color = Column(Text)


class Brand(DbUtils):
    __tablename__ = 'price_brand'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=True, comment='Brands name', unique=True)
    logo = Column(Text, nullable=True, comment='Url or path to brands logo')
    aggregate_rating = Column(
        Integer,
        nullable=True,
        comment='The overall rating, based on a collection of reviews or ratings, of the item'
    )
    review = Column(Text, nullable=True, comment='A review of the item. Supersedes reviews')
    slogan = Column(Text, nullable=True, comment='A slogan or motto associated with the item')
    alternate_name = Column(Text, nullable=True, comment='An alias for the item')
    description = Column(Text, nullable=True, comment='A description of the item')
    brands_url = Column(Text, nullable=True, comment='URL to brands page')

    def __init__(self, name, logo=None):
        self.name = name
        self.logo = logo if logo else None


class MetaCategory(DbUtils):
    __tablename__ = 'price_meta_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Mata category name', unique=True)
    logo = Column(Text, nullable=True, comment='Url or path to meta_category logo')
    description = Column(Text, nullable=True, comment='A description of the item')

    def __init__(self, name=None, created_by=None):
        self.name = name
        # self.created_by = created_by

    def __repr__(self):
        return '<MetaCategory {}> (Created By: {})'.format(self.name, self.created_by)


class Category(DbUtils):
    __tablename__ = 'price_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    meta_category_id = Column(
        Integer,
        ForeignKey("price_meta_category.id"),
        nullable=False,
        comment='FK to meta_category table'
    )
    name = Column(Text, nullable=False, comment='Brands name')
    logo = Column(Text, nullable=True, comment='Url or path to meta_category logo')
    description = Column(Text, nullable=True, comment='A description of the item')

    def __init__(self, name=None, meta_category_id=None):
        self.name = name
        self.meta_category_id = meta_category_id

    def __repr__(self):
        return '<Category %r>' % (self.name)


class Shop(DbUtils):
    __tablename__ = 'price_shop'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    url = Column(Text, nullable=False, comment='Url to shops page', unique=True)

    def __init__(self, url=None, created_by=None):
        self.url = url
        self.created_by = created_by

    def __repr__(self):
        return '<Shop %r>' % (self.url)


class EntryPoint(DbUtils):
    __tablename__ = 'price_entry_point'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    url = Column(Text, nullable=False, comment='Path to show wiyth category catalog', unique=True)
    category_id = Column(
        Integer,
        ForeignKey("price_category.id"),
        nullable=False,
        comment='FK to category table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_shop.id"),
        nullable=False,
        comment='FK to shop table'
    )
    description = Column(Text, nullable=True, comment='A description of the item')

    def __init__(self, url=None, category_id=None, shop_id=None):
        self.url = url
        self.category_id = category_id
        self.shop_id = shop_id

    def __repr__(self):
        return '<EntryPoint %r (%r:%r)>' % (self.url, self.shop_id, self.created_by)


class KeyWord(DbUtils):
    __tablename__ = 'price_key_word'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    value = Column(Text, nullable=False, comment='Key Word', unique=True)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<KeyWord Value="{}" ID="{}"> ID IDUSRR: {} Creation Date {}'.format(self.value, self.id, self.created_by, self.creation_date) # noqa E502


class KeyWordLink(DbUtils):
    __tablename__ = 'price_key_word_link'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    category_id = Column(
        Integer,
        ForeignKey("price_category.id"),
        nullable=False,
        comment='FK to category table'
    )
    key_word_id = Column(
        Integer,
        ForeignKey("price_key_word.id"),
        nullable=False,
        comment='FK to key_word table'
    )

    def __init__(self, category_id, key_word_id):
        self.category_id = category_id
        self.key_word_id = key_word_id

    def __repr__(self):
        return '<KeyWordLink> ({},{}, ID IDUSRR: {})'.format(self.category_id, self.key_word_id, self.created_by)


class TagWordLink(DbUtils):
    __tablename__ = 'price_tag_word_link'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to price_product table'
    )
    key_word_id = Column(
        Integer,
        ForeignKey("price_key_word.id"),
        nullable=False,
        comment='FK to key_word table'
    )

    def __init__(self, product_id, key_word_id):
        self.product_id = product_id
        self.key_word_id = key_word_id

    def __repr__(self):
        return '<KeyWordLink> ({},{}, ID IDUSRR: {})'.format(self.product_id, self.key_word_id, self.created_by)


class Product(DbUtils):
    __tablename__ = 'price_product'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Name of product')
    brand_id = Column(
        Integer,
        ForeignKey("price_brand.id"),
        nullable=False,
        comment='FK to brand table'
    )
    category_id = Column(
        Integer,
        ForeignKey("price_category.id"),
        nullable=False,
        comment='FK to category table'
    )
    description = Column(Text, nullable=True, comment='A description of the item')
    slug = Column(Text, nullable=False, comment='Slug of product for url, include category name')

    def __init__(self, name, brand_id, category_id):
        self.brand_id = brand_id
        self.name = name
        self.category_id = category_id

    def __repr__(self):
        return '<Product {}> Brand ID: {}'.format(self.name, self.brand_id)


"""
class ProductShop(DbUtils):
    __tablename__ = 'price_product_shop'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_shop.id"),
        nullable=False,
        comment='FK to shop table'
    )

    def __init__(self, product_id, shop_id):
        self.product_id = product_id
        self.shop_id = shop_id

    def __repr__(self):
        return '<Product {}> Brand ID: {}'.format(self.name, self.brand_id)
"""


class ImageRepo(DbUtils):
    __tablename__ = 'price_repo_image'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    control_sum = Column(Text)
    image = Column(Text)
    dimension = Column(Text)
    size = Column(Integer)
    orientation = Column(Text)
    main_color = Column(Text)


class ProductImage(DbUtils):
    __tablename__ = 'price_product_image'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )
    repo_image_id = Column(
        Integer,
        ForeignKey("price_repo_image.id"),
        nullable=False,
        comment='FK to images repository'
    )

    def __init__(self, product_id, repo_image_id):
        self.product_id = product_id
        self.repo_image_id = repo_image_id

    def __repr__(self):
        return '<ProductImage {} - {}>'.format(self.product_id, self.repo_image_id)


class ProductPrice(DbUtils):
    __tablename__ = 'price_product_price'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_repo_image.id"),
        nullable=False,
        comment='FK to images repository'
    )
    date_price = Column(Date, nullable=False, comment='Date for registration product price')
    price = Column(Numeric(10, 2), nullable=False, comment='Price for product')

    __table_args__ = (
        db.UniqueConstraint(
            'product_id',
            'shop_id',
            'date_price',
            name='uniq_product_id_shop_id_date_price'
        ),
    )

    def __init__(self, product_id, shop_id, price, date_price):
        self.product_id = product_id
        self.shop_id = shop_id
        self.price = price
        self.date_price = date_price

    def __repr__(self):
        return '<ProductPrice {}> Product ID {} Date {}'.format(self.price, self.product_id, self.date_price)


class ProductShopUrl(DbUtils):
    __tablename__ = 'price_product_shop_url'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_repo_image.id"),
        nullable=False,
        comment='FK to images repository'
    )
    url = Column(Text, nullable=False, comment='Url to products page')
    __table_args__ = (
        db.UniqueConstraint(
            'product_id',
            'shop_id',
            'url',
            name='uniq_product_id_shop_id_url'
        ),
    )

    def __init__(self, url, product_id, shop_id):
        self.url = url
        self.product_id = product_id
        self.shop_id = shop_id

    def __repr__(self):
        return '<EntryPoint %r (%r:%r)>' % (self.url, self.product_by, self.shop_id)
