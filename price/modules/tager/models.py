from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy import Sequence, Index
from price.utils.models import DbUtils


import logging
log = logging.getLogger(__name__)


class TagerBrandAssignment(DbUtils):

    __tablename__ = 'tager_brand_assignment'
    __seqname__ = '{}_id_seq'.format(__tablename__)
    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table',
        unique=True
    )
    brand = Column(Text, nullable=False, comment='Brand Name')
    tager_brand_id = Column(
        Integer,
        ForeignKey("tager_brand.id"),
        nullable=True,
        comment='FK to tager_brand.id table',
        unique=False
    )

    def __init__(self, imp_catalog_page_id, brand, tager_brand_id):
        if brand is None or brand == '':
            raise ValueError('Field brand can\'t be empty')
        self.imp_catalog_page_id = imp_catalog_page_id
        self.brand = brand
        self.tager_brand_id = tager_brand_id

    def __repr_(self):
        return '<TagerBrandAssignment {} {}'.format(self.imp_catalog_page_id, self.brand)


tager_brand_assignment_brand_idx = Index('tager_brand_assignment_brand_idx', TagerBrandAssignment.brand)


class TagerContext(DbUtils):
    __tablename__ = 'tager_context'
    __seqname__ = '{}_id_seq'.format(__tablename__)
    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Context definition')

    def __init__(self, name):
        if name and len(name) != 0:
            self.name = name.lower()
        else:
            raise ValueError('Field "name" can\'t by empty')

    def __repr__(self):
        return '<TagerContext {}>'.format(self.name)


class TagerTag(DbUtils):
    __tablename__ = 'tager_tag'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    value = Column(Text, nullable=False, comment='Main tag')
    tager_context_id = Column(
        Integer,
        ForeignKey("tager_context.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table, The context of the use of the tag',
        unique=False
    )

    def __init__(self, tager_context_id, value):
        if value is None or value == '':
            raise ValueError('Field value can\'t be empty')
        if tager_context_id is None:
            raise ValueError('Field tager_context_id can\'t be empty')
        self.tager_context_id = tager_context_id
        self.value = value

    def __repr_(self):
        return '<TagerTag {} {}'.format(self.tager_context_id, self.value)


tager_tag_value_idx = Index('tager_tag_value_idx', TagerTag.value)


class TagerTagSynonym(DbUtils):
    __tablename__ = 'tager_tag_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    value = Column(Text, nullable=False, comment='Tag value synonym')
    tager_tag_id = Column(
        Integer,
        ForeignKey("tager_tag.id"),
        nullable=False,
        comment='FK to tager_tag.id table',
        unique=False
    )

    def __init__(self, tager_tag_id, value):
        if value is None or value == '':
            raise ValueError('Field value can\'t be empty')
        if tager_tag_id is None:
            raise ValueError('Field tager_tag_id can\'t be empty')
        self.tager_tag_id = tager_tag_id
        self.value = value

    def __repr_(self):
        return '<TagerTagSynonym {} {}'.format(self.tager_tag_id, self.value)


tager_tag_synonym_value_idx = Index('tager_tag_synonym_value_idx', TagerTagSynonym.value)


class TagerCategory(DbUtils):
    __tablename__ = 'tager_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Category  name')

    def __init__(self, name):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name

    def __repr__(self):
        return '<TagerCategory {}>'.format(self.name)


tager_category_name_idx = Index('tager_category_name_idx', TagerCategory.name)


class TagerCategorySynonym(DbUtils):
    __tablename__ = 'tager_category_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    tager_category_id = Column(
        Integer,
        ForeignKey("tager_category.id"),
        nullable=False,
        comment='FK to tager_category.id table'
    )
    value = Column(Text, nullable=True, comment='Category synonym')

    def __init__(self, tager_category_id, value):
        if tager_category_id is None:
            raise ValueError('Field tager_category_id can\'t be empty')

        if value is None or value == '':
            raise ValueError('Field value can\'t be empty')

        self.tager_category_id = tager_category_id
        self.value = value

    def __repr__(self):
        return '<TagerCategorySynonym tager_category_id: {} value: {}'.format(
            self.tager_category_id,
            self.value
        )


tager_category_synonym_value_idx = Index('tager_category_synonym_value_idx', TagerCategorySynonym.value)


class TagerCategoryAssignment(DbUtils):

    __tablename__ = 'tager_category_assignment'
    __seqname__ = '{}_id_seq'.format(__tablename__)
    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table'
    )
    category = Column(Text, nullable=False, comment='Brand Name')
    rate = Column(Integer, nullable=False, comment='Index of the probability of indicating the category')

    def __init__(self, imp_catalog_page_id, category, rate):
        if category is None or category == '':
            raise ValueError('Field category can\'t be empty')
        if rate is None:
            raise ValueError('Field rate can\'t be None')
        self.imp_catalog_page_id = imp_catalog_page_id
        self.category = category
        self.rate = rate

    def __repr__(self):
        return '<TagerCategoryAssignment {} {} #{}'.format(
            self.imp_catalog_page_id,
            self.category,
            self.rate
        )


class TagerBrand(DbUtils):
    __tablename__ = 'tager_brand'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Brands name', unique=True)

    def __init__(self, name):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name

    def __repr__(self):
        return '<TagerBrand {}>'.format(self.name)


tager_brand_name_idx = Index('tager_brand_name_idx', TagerBrand.name)


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
    value = Column(Text, nullable=False, comment='Brands synonym')

    def __init__(self, tager_brand_id, value):
        if value is None or value == '':
            raise ValueError('Field value can\'t be empty')
        if tager_brand_id is None:
            raise ValueError('Field tager_brand_id can\'t be empty')
        self.value = value
        self.tager_brand_id = tager_brand_id

    def __repr__(self):
        return '<TagerBrandSynonym {} brand_id: {}'.format(self.value, self.tager_brand_id)


tager_brand_synonym_value_idx = Index('tager_brand_synonym_value_idx', TagerBrandSynonym.value)


class TagerColor(DbUtils):
    __tablename__ = 'tager_color'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='polish color name')

    def __init__(self, name):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        self.name = name

    def __repr__(self):
        return '<TagerColor {}>'.format(self.name)


class TagerColorSynonym(DbUtils):
    __tablename__ = 'tager_color_synonym'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    tager_color_id = Column(
        Integer,
        ForeignKey("tager_color.id"),
        nullable=False,
        comment='FK to tager_color.id table'
    )
    value = Column(Text, nullable=False, comment='Color synonym')

    def __init__(self, tager_color_id, value):
        if value is None or value == '':
            raise ValueError('Field value can\'t be empty')
        if tager_color_id is None:
            raise ValueError('Field tager_color_id can\'t be empty')
        self.value = value
        self.tager_color_id = tager_color_id

    def __repr__(self):
        return '<TagerColorSynonym {} brand_id: {}'.format(self.value, self.tager_color_id)


tager_color_synonym_value_idx = Index('tager_color_synonym_value_idx', TagerColorSynonym.value)


class TagerSize(DbUtils):
    __tablename__ = 'tager_size'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Key Word', unique=True)
    meaning = Column(Text, nullable=True, comment='Meaning word using to grouping')

    def __init__(self, name, meaning):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        if meaning is None or meaning == '':
            raise ValueError('Field meaning can\'t be empty')
        self.name = name.lower()
        self.meaning = meaning.lower()

    def __repr__(self):
        return '<TagerSize ID: {}, name: {}, meaning: {}>'.format(
            self.id,
            self.name,
            self.meaning
        )


class TagerTaggingResult(DbUtils):
    __tablename__ = 'tager_tagging_result'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table'
    )
    name = Column(Text, nullable=False, comment='product namee')
    orginal_title = Column(Text, nullable=False, comment='orginal title')
    brand = Column(Text, nullable=False, comment='brands name')

    def __init__(self, imp_catalog_page_id, name, orginal_title, brand):
        if imp_catalog_page_id is None:
            raise ValueError('Field imp_catalog_page_id can\'t be empty')
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        if orginal_title is None or orginal_title == '':
            raise ValueError('Field orginal_title can\'t be empty')
        if brand is None or brand == '':
            raise ValueError('Field brand can\'t be empty')
        self.imp_catalog_page_id = imp_catalog_page_id
        self.name = name
        self.orginal_title = orginal_title
        self.brand = brand

    def __repr__(self):
        return '<TagerTaggingResult IcpID: {} Title {}'.format(self.imp_catalog_page_id, self.name)


tager_tagging_result_imp_catalog_page_id_idx = Index(
    'tager_tagging_result_imp_catalog_page_id_idx',
    TagerTaggingResult.imp_catalog_page_id
)
