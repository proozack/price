from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String, Numeric, Date, Boolean
from sqlalchemy import Sequence
from sqlalchemy.dialects.postgresql import JSONB


import logging
log = logging.getLogger(__name__)

class TagerContext(DbUtils):
    __tablename__ = 'tager_context'
    __seqname__ = '{}_id_seq'.format(__tablename__)
    name = Column(Text, nullable=False, comment='Context definition')

class TagerKeys(DbUtils):
    __tablename__ = 'tager_keys'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    value = Column(Text, nullable=False, comment='Main tag')
    meaning = Column(Text, nullable=False, comment='Main tag')
    main_value = Column(Text, nullable=False, comment=' czy to jest potrzebne ???')

class TagerTag(DbUtils):
    __tablename__ = 'tager_tag'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    value = Column(Text, nullable=False, comment='Tag value synonym')
    meaning = Column(Text, nullable=False, comment='Tags meaning')
    tager_keys_id = = Column(
        Integer,
        ForeignKey("tager_keys.id"),
        nullable=False,
        comment='FK to tager_keys.id table',
        unique=True
    )
    tager_context_id = = Column(
        Integer,
        ForeignKey("tager_context.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table, The context of the use of the tag',
        unique=True
    )
    context = Column(Text, nullable=False, comment='The context of the use of the tag')
    context_value = Column(Text, nullable=False, comment='context - loose link')


class TagerCategory(DbUtils):
    __tablename__ = 'def_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Category  name')


class TagerCategorySynonym(DbUtils):
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
    __tablename__ = 'tager_brand'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=True, comment='Brands name', unique=True)


class TagerBrandSynonym(DbUtils):
    __tablename__ = 'tager_brand_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    tager_brand_id = Column(
        Integer,
        ForeignKey("tager_brand.id"),
        nullable=False,
        comment='FK to tager_category.id table'
    )
    value = Column(Text, nullable=True, comment='Brands synonym')


class TagerColor(DbUtils):
    __tablename__ = 'tager_color'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='polish color name')


class TagerSize(DbUtils):
    __tablename__ = 'tager_size'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Key Word', unique=True)
    meaning = Column(Text, nullable=True, comment='Meaning word using to grouping')
