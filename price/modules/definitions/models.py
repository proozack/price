from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String, Numeric, Date, Boolean
from sqlalchemy import Sequence
from sqlalchemy.dialects.postgresql import JSONB


import logging
log = logging.getLogger(__name__)


class DefCategory(DbUtils):
    __tablename__ = 'def_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Category  name')
    logo = Column(Text, nullable=True, comment='Url or path to categorys logo')
    description = Column(Text, nullable=True, comment='A description of the item')
    slug = Column(Text, nullable=True, comment='Slug of category for url')
    parent = Column(
        Integer,
        ForeignKey("def_category.id"),
        nullable=False,
        comment='FK to meta_category table'
    )

class DefCategorySynonym(DbUtils):
    __tablename__ = 'def_category_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    def_category_id = Column(
        Integer,
        ForeignKey("def_category.id"),
        nullable=False,
        comment='FK to def_category.id table'
    )
    value = Column(Text, nullable=True, comment='Category synonym')


class DefBrand(DbUtils):
    __tablename__ = 'def_brand'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=True, comment='Brands name', unique=True)
    logo = Column(Text, nullable=True, comment='Url or path to brands logo')
    slogan = Column(Text, nullable=True, comment='A slogan or motto associated with the item')
    description = Column(Text, nullable=True, comment='A description of the item')
    brands_url = Column(Text, nullable=True, comment='URL to brands page')

class DefBrandSynonym(DbUtils):
    __tablename__ = 'def_brand_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    def_brand_id = Column(
        Integer,
        ForeignKey("def_brand.id"),
        nullable=False,
        comment='FK to def_category.id table'
    )
    value = Column(Text, nullable=True, comment='Brands synonym')

