from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String, Numeric, Date, Boolean
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


class OfertArch(DbUtils):
    __tablename__ = 'price_ofert_arch'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    last_id = Column(Integer, nullable=False, comment='Id from price_ofert')
    entry_point_id = Column(
        Integer,
        ForeignKey("price_entry_point.id"),
        nullable=False,
        comment='FK to entry_point_id table'
    )
    title = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    image = Column(Text, nullable=False)
    manufacturer = Column(Text, nullable=True)

    def __init__(self, last_id, entry_point_id, title, price, currency, url, image, manufacturer):
        self.last_id = last_id
        self.entry_point_id = entry_point_id
        self.title = title
        self.price = price
        self.currency = currency
        self.url = url
        self.image = image
        self.manufacturer = manufacturer

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
    slug = Column(Text, nullable=True, comment='Slug of category for url')

    def __init__(self, name=None, meta_category_id=None, slug=None):
        self.name = name
        self.meta_category_id = meta_category_id
        self.slug = slug

    def __repr__(self):
        return '<Category %r>' % (self.name)

class CategorySynonym(DbUtils):
    __tablename__ = 'price_category_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    category_id = Column(
        Integer,
        ForeignKey("price_category.id"),
        nullable=False,
        comment='FK to category table'
    )
    value = Column(Text, nullable=False, comment='Category synonym name')

    def __init__(self, category_id, value):
        self.category_id = category_id
        self.value = value

    def __repr__(self):
        return '<CategorySynonym %r>' % (self.value)


class Shop(DbUtils):
    __tablename__ = 'price_shop'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    url = Column(Text, nullable=False, comment='Url to shops page', unique=True)
    is_brand_shop = Column(Boolean, nullable=True, comment='Information about is a brand shop or no')

    def __init__(self, url=None, created_by=None):
        self.url = url
        self.created_by = created_by
        self.is_brand_shop = False

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
    product_version_id = Column(
        Integer,
        ForeignKey("price_product_version.id"),
        nullable=False,
        comment='FK to product table'
    )
    key_word_id = Column(
        Integer,
        ForeignKey("price_key_word.id"),
        nullable=False,
        comment='FK to key_word table'
    )

    def __init__(self, product_version_id, key_word_id):
        self.product_version_id = product_version_id
        self.key_word_id = key_word_id

    def __repr__(self):
        return '<KeyWordLink> ({},{}, ID IDUSRR: {})'.format(self.product_id, self.key_word_id, self.created_by)


class TagOfert(DbUtils):
    __tablename__ = 'price_tag_ofert'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    ofert_id = Column(
        Integer,
        ForeignKey("price_ofert.id"),
        nullable=False,
        comment='FK to ofert table'
    )
    tag_product_def_id = Column(
        Integer,
        ForeignKey("price_tag_product_def.id"),
        nullable=False,
        comment='FK to price_tag_product_def table'
    )

    def __init__(self, ofert_id, tag_product_def_id):
        self.ofert_id = ofert_id
        self.tag_product_def_id = tag_product_def_id

    def __repr__(self):
        return '<TagOfert> ({},{}, ID IDUSR: {})'.format(self.ofer_id, self.tag_product_def_id, self.created_by)



class TagProductDef(DbUtils):
    __tablename__ = 'price_tag_product_def'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    category_id = Column(
        Integer,
        ForeignKey("price_category.id"),
        nullable=False,
        comment='FK to category table'
    )
    brand_id = Column(
        Integer,
        ForeignKey("price_brand.id"),
        nullable=False,
        comment='FK to brand table'
    )

    def __init__(self, category_id, brand_id):
        self.category_id = category_id
        self.brand_id = brand_id

    def __repr__(self):
        return '<TagProductDef {}>)'.format(self.id)


class TagProduct(DbUtils):
    __tablename__ = 'price_tag_product'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    tag_product_def_id = Column(
        Integer,
        ForeignKey("price_tag_product_def.id"),
        nullable=False,
        comment='FK to price_tag_product_def table'
    )
    tag_id = Column(
        Integer,
        ForeignKey("price_tag.id"),
        nullable=False,
        comment='FK to tag table'
    )

    def __init__(self, tag_product_def_id, tag_id):
        self.tag_product_def_id = tag_product_def_id
        self.tag_id = tag_id

    def __repr__(self):
        return '<TagProduct> ({},{}, ID IDUSRR: {})'.format(self.tag_product_def_id, self.tag_id, self.created_by)


class Tag(DbUtils):
    __tablename__ = 'price_tag'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    value = Column(Text, nullable=False, comment='Key Word', unique=True)
    meaning = Column(Text, nullable=True, comment='Meaning word using to grouping')

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Tag Value="{}" ID="{}"> ID IDUSRR: {} Creation Date {}'.format(self.value, self.id, self.created_by, self.creation_date) # noqa E502



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

    def __init__(self, name, brand_id, category_id, slug, is_standard = False):
        self.brand_id = brand_id
        self.name = name
        self.category_id = category_id
        self.slug = slug
        self.is_standard = is_standard

    def __repr__(self):
        return '<Product {}> Brand ID: {}'.format(self.name, self.brand_id)


class ProductStatement(DbUtils):
    __tablename__ = 'price_product_statement'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(
        Integer,
        Sequence(__seqname__),
        primary_key=True
    )
    ofert_arch_id = Column(
        Integer,
        ForeignKey("price_ofert_arch.id"),
        nullable=False,
        comment='FK to arch ofert'
    )
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
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )
    product_version_id = Column(
        Integer,
        ForeignKey("price_product_version.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_shop.id"),
        nullable=False,
        comment='FK to shop repository'
    )
    product_image_id = Column(
        Integer,
        ForeignKey("price_product_image.id"),
        nullable=False,
        comment='FK to images'
    )
    product_shop_url_id = Column(
        Integer,
        ForeignKey("price_product_shop_url.id"),
        nullable=False,
        comment='FK to shops\'s url'
    )
    product_price_id = Column(
        Integer,
        ForeignKey("price_product_price.id"),
        nullable=False,
        comment='FK to producct\'s price'
    )
    def __repr__(self):
        return '<ProductStatement {} - {}>'.format(self.id, self.ofert_arch_id)

    def __init__(self, ofert_arch_id, brand_id, category_id, product_id, poduct_version_id, shop_id, product_image_id, product_shop_url_id, product_price_id):
        self.ofert_arch_id = ofert_arch_id
        self.brand_id = brand_id
        self.category_id = category_id
        self.product_id = product_id
        self.product_version_id = product_version_id
        self.shop_id = shop_id
        self.product_image_id = product_image_id
        self.product_shop_url_id = product_shop_url_id
        self.product_price_id = product_price_id 


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
    __table_args__ = (
        db.UniqueConstraint(
            'image',
            name='uniq_product_image'
        ),
    )

    def __init__(self, image, control_sum):
        self.control_sum = control_sum
        self.image = image

    def __repr__(self):
        return '<ImageRepo #[{}] url: {}>'.format(self.control_sum, self.image)


class ProductImage(DbUtils):
    __tablename__ = 'price_product_image'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_version_id = Column(
        Integer,
        ForeignKey("price_product_version.id"),
        nullable=False,
        comment='FK to product table'
    )
    repo_image_id = Column(
        Integer,
        ForeignKey("price_repo_image.id"),
        nullable=False,
        comment='FK to images repository'
    )

    def __init__(self, product_version_id, repo_image_id):
        self.product_version_id = product_version_id
        self.repo_image_id = repo_image_id

    def __repr__(self):
        return '<ProductImage {} - {}>'.format(self.product_id, self.repo_image_id)


class ProductVersion(DbUtils):
    __tablename__ = 'price_product_version'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("price_product.id"),
        nullable=False,
        comment='FK to product table'
    )

    def __init__(self, product_id): 
        self.product_id = product_id

    def __repr__(self):
        return '<ProductVersion {} - {}'.format(self.product_id)


class ProductPrice(DbUtils):
    __tablename__ = 'price_product_price'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_version_id = Column(
        Integer,
        ForeignKey("price_product_version.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_shop.id"),
        nullable=False,
        comment='FK to images repository'
    )
    date_price = Column(Date, nullable=False, comment='Date for registration product price')
    price = Column(Numeric(10, 2), nullable=False, comment='Price for product')

    __table_args__ = (
        db.UniqueConstraint(
            'product_version_id',
            'shop_id',
            'date_price',
            name='uniq_product_id_shop_id_date_price'
        ),
    )

    def __init__(self, product_version_id, shop_id, price, date_price):
        self.product_version_id = product_version_id
        self.shop_id = shop_id
        self.price = price
        self.date_price = date_price

    def __repr__(self):
        return '<ProductPrice {}> Product ID {} Date {}'.format(self.price, self.product_id, self.date_price)


class ProductShopUrl(DbUtils):
    __tablename__ = 'price_product_shop_url'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_version_id = Column(
        Integer,
        ForeignKey("price_product_version.id"),
        nullable=False,
        comment='FK to product table'
    )
    shop_id = Column(
        Integer,
        ForeignKey("price_shop.id"),
        nullable=False,
        comment='FK to shop repository'
    )
    url = Column(Text, nullable=False, comment='Url to products page')
    __table_args__ = (
        db.UniqueConstraint(
            'product_version_id',
            'shop_id',
            'url',
            name='uniq_product_id_shop_id_url'
        ),
    )

    def __init__(self, url, product_version_id, shop_id):
        self.url = url
        self.product_version_id = product_version_id
        self.shop_id = shop_id

    def __repr__(self):
        return '<EntryPoint %r (%r:%r)>' % (self.url, self.product_by, self.shop_id)


class Color(DbUtils):
    __tablename__ = 'res_color'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='polish color name')
    hexadecimal = Column(Text, nullable=False, comment='color in hex')
    r = Column(Integer, nullable=False, comment='read color')
    g = Column(Integer, nullable=False, comment='green color')
    b = Column(Integer, nullable=False, comment='blue color')


class Size(DbUtils):
    __tablename__ = 'res_size_dict'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Key Word', unique=True)
    meaning = Column(Text, nullable=True, comment='Meaning word using to grouping')
