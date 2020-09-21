from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Float
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Sequence

from app.utils.models import DbUtils
from datetime import datetime
import logging
log = logging.getLogger(__name__)


class UserBase(DbUtils):
    __abstract__ = True

    user_name = Column(String(50), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    user_type = Column(Integer, index=True, nullable=False, default=1)
    avatar = Column(String(200), nullable=True)
    passwd = Column(String(300), index=True, unique=False)
    pas_change_req = Column(Boolean, nullable=False, default=False)
    next_pas_change = Column(Date, nullable=True, default=datetime.now())
    is_authenticated = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    is_anonymous = Column(Boolean, nullable=False, default=False)


class User(UserBase):
    __tablename__ = 'ims_users'

    def __init__(self, name=None, email=None, passwd=None):
        self.user_name = name
        self.passwd = passwd
        self.email = email
        self.created_by = 1

    def __repr__(self):
        return '<User %r>' % (self.user_name)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id


class UserArch(UserBase):
    """Tabela archiwalna dla tabeli users"""
    __tablename__ = 'ims_users_arch'


class WorkerBase(DbUtils):
    __abstract__ = True
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdays = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    sex = Column(String(1), nullable=False, default='M')
    # user_id = Column(Integer, ForeignKey('ims_users.id'))

    @declared_attr
    def users_id(cls):
       return Column(ForeignKey('ims_users.id'))  # noqa E111

    @declared_attr
    def user(cls):
        return relationship("User")


class Worker (WorkerBase):
    __tablename__ = 'ims_workers'

    def __init__(self, first_name=None, last_name=None, sex=None):
        self.first_name = first_name
        self.last_name = last_name
        self.created_by = 1
        self.sex = sex

    def __repr__(self):
        return '<Worker %r %r>' % (self.first_name, self.last_name)


class ArchWorker(WorkerBase):
    """Tabela archiwalna dla tabeli users"""
    __tablename__ = 'ims_workers_arch'


class AuthLog(DbUtils):
    __tablename__ = 'ims_auth_log'

    login_used = Column(String(50), nullable=False)
    if_loged = Column(Boolean, nullable=False)
    message = Column(Text, nullable=True)

    def __init__(self, login_used=None, if_loged=False, message='authentication will not succeed'):
        self.login_used = login_used
        self.if_loged = if_loged
        self.created_by = 1
        self.message = message

    def __repr__(self):
        return '<Auth %r %r>' % (self.login_used, self.if_loged)


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
    name = Column(Text, nullable=True, comment='Brands name')
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


class MetaCategory(DbUtils):
    __tablename__ = 'price_meta_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Mata category name')
    logo = Column(Text, nullable=True, comment='Url or path to meta_category logo')
    description = Column(Text, nullable=True, comment='A description of the item')

    def __init__(self, name=None, created_by=None):
        self.name = name
        self.created_by = created_by

    def __repr__(self):
        return '<MetaCategory %r>' % (self.name)


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

    def __init__(self, name=None, meta_category_id=None, created_by=None):
        self.name = name
        self.meta_category_id = meta_category_id
        self.created_by = created_by

    def __repr__(self):
        return '<Category %r>' % (self.name)


class Shop(DbUtils):
    __tablename__ = 'price_shop'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    url = Column(Text, nullable=False, comment='Url to shops page')

    def __init__(self, url=None, created_by=None):
        self.url = url
        self.created_by = created_by

    def __repr__(self):
        return '<Shop %r>' % (self.url)


class EntryPoint(DbUtils):
    __tablename__ = 'price_entry_point'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    url = Column(Text, nullable=False, comment='Path to show wiyth category catalog')
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

    def __init__(self, url=None, category_id=None, shop_id=None, created_by=None):
        self.url = url
        self.category_id = category_id
        self.shop_id = shop_id
        self.created_by = created_by

    def __repr__(self):
        return '<EntryPoint %r (%r:%r)>' % (self.url, self.shop_id, self.created_by)
