from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String
from sqlalchemy import Sequence
from app.utils.models import DbUtils


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
        # self.created_by = Config.PRICE_USER_ID
        # self.creation_date = datetime.now()

    def __repr__(self):
        return '<KeyWordLink> ({},{}, ID IDUSRR: {})'.format(self.category_id, self.key_word_id, self.created_by)
