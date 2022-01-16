from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy import Sequence
from price.utils.models import DbUtils


import logging
log = logging.getLogger(__name__)


class DefTypeCategory(DbUtils):
    __tablename__ = 'def_type_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Type category eg. She / He')

    def __init__(self, name):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name

    def __repr__(self):
        return '<DefTypeCategory name: {}>'.format(self.name)


class DefGroupCategory(DbUtils):
    __tablename__ = 'def_group_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    def_type_category_id = Column(
        Integer,
        ForeignKey("def_type_category.id"),
        nullable=False,
        comment='FK todef_type_category.id table'
    )
    name = Column(Text, nullable=False, comment='Groups category name')
    logo = Column(Text, nullable=True, comment='Url or path to categorys group logo')
    description = Column(Text, nullable=True, comment='A description of the item')
    slug = Column(Text, nullable=True, comment='Slug of category for url')

    def __init__(self, def_type_category_id, name, logo=None, description=None, slug=None):
        if def_type_category_id is None:
            raise ValueError('Field name can\'t be empty')
        self.def_type_category_id = def_type_category_id
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name
        self.logo = logo
        self.description = description
        self.slug = slug

    def __repr__(self):
        return '<DefGroupCategory name: {} def_type_category_id: {}>'.format(self.name, self.def_type_category_id)


class DefMetaCategory(DbUtils):
    __tablename__ = 'def_meta_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    def_group_category_id = Column(
        Integer,
        ForeignKey("def_group_category.id"),
        nullable=False,
        comment='FK to def_group_category.id table'
    )
    name = Column(Text, nullable=False, comment='Category  name')
    logo = Column(Text, nullable=True, comment='Url or path to categorys logo')
    description = Column(Text, nullable=True, comment='A description of the item')
    slug = Column(Text, nullable=True, comment='Slug of category for url')

    def __init__(self, def_group_category_id, name, logo=None, description=None, slug=None):
        if def_group_category_id is None:
            raise ValueError('Field name can\'t be empty')
        self.def_group_category_id = def_group_category_id
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name
        self.logo = logo
        self.description = description
        self.slug = slug

    def __repr__(self):
        return '<DefMetaCategory name: {} def_group_category_id: {}>'.format(self.name, self.def_group_category_id)


class DefBrand(DbUtils):
    __tablename__ = 'def_brand'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Brands name', unique=True)
    logo = Column(Text, nullable=True, comment='Url or path to brands logo')
    slogan = Column(Text, nullable=True, comment='A slogan or motto associated with the item')
    description = Column(Text, nullable=True, comment='A description of the item')
    brands_url = Column(Text, nullable=True, comment='URL to brands page')

    def __init__(self, name, logo=None, slogan=None, description=None, brands_url=None):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name
        self.logo = logo
        self.slogan = slogan
        self.description = description
        self.brands_url = brands_url

    def __repr__(self):
        return '<DefBrand name: {}'.format(self.name)
