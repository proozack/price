from sqlalchemy import Column, Float, Integer, Text, ForeignKey, String, Numeric, Date, Boolean
from sqlalchemy import Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func, Index
from datetime import datetime
from price import db
from price.utils.models import DbUtils


import logging
log = logging.getLogger(__name__)


class ImpCatalogPage(DbUtils):
    __tablename__ = 'imp_catalog_page'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    entry_point_id = Column(
        Integer,
        ForeignKey("price_entry_point.id"),
        nullable=False,
        comment='FK to entry_point_id table'
    )
    url = Column(Text, nullable=False, comment='url to product')
    title = Column(Text, nullable=False, comment='Product title form catalog page')
    img = Column(Text, nullable=True, comment='url to main image')
    brand = Column(Text, nullable=True, comment='Brand Name')
    
    def __init__(self, entry_point_id, url, title, img, brand):
        self.entry_point_id = entry_point_id
        self.url = url
        self.title = title
        self.img = img
        self.brand = brand

    def __repr__(self):
        return '<ImpCatalogPage {} - {} EpID: {}>'.format(self.brand, self.title, self.entry_point_id)

idx_url = Index('imp_catalog_page_url_idx', ImpCatalogPage.url)

class ImpCatalogPageStatus(DbUtils):
    __tablename__ = 'imp_catalog_page_status'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table',
        unique=True
    )
    # specific_brand_date = Column(Date, nullable=True, comment='Specific brand date')
    # specific_category_date = Column(Date, nullable=True, comment='Tagged date')
    specific_brand_date = Column(db.DateTime, nullable=True, comment='Specific brand date')
    specific_category_date = Column(db.DateTime, nullable=True, comment='Tagged date')

    def __init__(self, imp_catalog_page_id, tagged_date=None, specific_brand_date=None):
        self.imp_catalog_page_id = imp_catalog_page_id
        self.tagged_date = tagged_date
        self.specific_brand_date = specific_brand_date

    def __repr__(self):
        return '<ImpCatalogPageStatus CatalogPage: {} Tagged Date: {} Brand Date: {}'.format(self.imp_catalog_page_id, self.tagged_date, self.specific_brand_date)

class ImpProductPage(DbUtils):
    __tablename__ = 'imp_product_page'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table',
        unique=True
    )
    description = Column(Text, nullable=True, comment='Product description')
    title = Column(Text, nullable=True, comment='Product title from product page')
    size = Column(JSONB, nullable=True, comment='List available products sizes')
    brand = Column(Text, nullable=True, comment='Brand Name')
    composition = Column(Text, nullable=True, comment='Product composition')
    color = Column(JSONB, nullable=True, comment='List available products color')
    attributes = Column(JSONB, nullable=True, comment='List attributes')
    images = Column(JSONB, nullable=True, comment='List Images')
    category = Column(Text, nullable=True, comment='Product category')

    def __init__(self,
                 imp_catalog_page_id,
                 description=None,
                 title=None,
                 size=[],
                 brand=None,
                 composition=[],
                 color=[],
                 attributes=[],
                 images=[],
                 category=None
                ):

        self.imp_catalog_page_id = imp_catalog_page_id
        self.description = description
        self.title = title
        self.size = size
        self.brand = brand
        self.composition = composition
        self.color = color
        self.attributes = attributes
        self.images = images
        self.category = category

    def __init__(self):
        pass

    def __repr__(self):
        return '<ImpProductPage {}: {}>'.format(self.imp_catalog_page_id, self.title)


class ImpProductPrice(DbUtils):
    __tablename__ = 'imp_product_price'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    imp_catalog_page_id = Column(
        Integer,
        ForeignKey("imp_catalog_page.id"),
        nullable=False,
        comment='FK to imp_catalog_page.id table'
    )
    price = Column(Float, nullable=False, comment='Product price')
    scan_date = Column(Date, nullable=False, comment='Scan date')
    currency = Column(String, nullable=False, comment='Product price Currency')


    def __init__(self, imp_catalog_page_id,  price, currency, scan_date=datetime.now()):
        self.imp_catalog_page_id = imp_catalog_page_id
        self.price = price
        self.currency = currency
        self.scan_date = scan_date

    def __repr__(self):
        return '<ImpProductPrice ID:{} DATE:{} - {} {}>'.format(self.imp_catalog_page_id, self.scan_date, self.price, self.currency)

idx_imp_catalog_page_id = Index('imp_product_price_imp_catalog_page_id_idx', ImpProductPrice.imp_catalog_page_id)
idx_scan_date = Index('imp_product_price_scan_date_idx', ImpProductPrice.scan_date)
