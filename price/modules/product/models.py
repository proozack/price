from sqlalchemy import Column, Integer, Text, ForeignKey, Date, Float, String
from sqlalchemy import Sequence, Index
from price.utils.models import DbUtils


import logging
log = logging.getLogger(__name__)


class ProductDefinition(DbUtils):
    __tablename__ = 'product_definition'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='Product name')
    ean = Column(Text, nullable=True, comment='Product ean number')
    brand = Column(Text, nullable=False, comment='Brand Name')
    collection = Column(Text, nullable=True, comment='Collection Name')

    def __init__(self, name, brand):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        if brand is None or name == '':
            raise ValueError('Field brand can\'t be empty')

        self.name = name
        self.brand = brand

    def __repr__(self):
        return '<ProductDefinition #id={}; name: {}, brand: {}>'.format(self.id, self.name, self.brand)


product_definition_name_idx = Index(
    'product_definition_name_idx',
    ProductDefinition.name
)

product_definition_brand_idx = Index(
    'product_definition_brand_idx',
    ProductDefinition.brand
)


class ProductImg(DbUtils):
    __tablename__ = 'product_img'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_definition_id = Column(
        Integer,
        ForeignKey("product_definition.id"),
        nullable=False,
        comment='FK to product_definition.id table, extension product definition on images domain'
    )
    path_big = Column(Text, nullable=True, comment='Path to image')
    path_thumbs = Column(Text, nullable=False, comment='Path to image')
    size_h = Column(Integer, nullable=True, comment='Images hight')
    size_w = Column(Integer, nullable=True, comment='Images width')
    orientation = Column(String(1), nullable=True, comment='Images orientation')
    main_color = Column(String(10), nullable=True, comment='Color of centroids')
    general_color = Column(String(10), nullable=True, comment='The most common color')
    control_sum_a1 = Column(String(256), nullable=True, comment='Control sum algorithm 1')
    control_sum_a2 = Column(String(256), nullable=True, comment='ontrol sum algorithm 2')
    control_sum_a32 = Column(String(256), nullable=True, comment='Control sum algorithm 3')
    img_source = Column(String(100), nullable=False, comment='Images source')
    orginal_images_id = Column(Integer, nullable=False, comment='Orginal images id')

    def __init__(self, product_definition_id, path_thumbs, img_source, orginal_images_id, path_big=None):
        if product_definition_id is None:
            raise ValueError('Field product_definition_id can\'t be None')
        if path_thumbs is None:
            raise ValueError('Field path_thumbs can\'t be None')
        if img_source is None:
            raise ValueError('Field img_source can\'t be None')
        if orginal_images_id is None:
            raise ValueError('Field orginal_images_id can\'t be None')

        self.product_definition_id = product_definition_id
        self.path_thumbs = path_thumbs
        self.img_source = img_source
        self.orginal_images_id = orginal_images_id
        self.path_big = path_big

    def __repr__(self):
        return '<ProductImg product_definition_id: {}, path: {}, img_source: {}, orginal_images_id: {}>'.format(
            self.product_definition_id,
            self.path_thumbs,
            self.img_source,
            self.orginal_images_id
        )


product_img_name_idx = Index(
    'product_img_orginal_images_ididx',
    ProductImg.orginal_images_id
)


product_img_img_source_idx = Index(
    'product_img_img_source_idx',
    ProductImg.img_source
)


class ProductShop(DbUtils):
    __tablename__ = 'product_shop'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_definition_id = Column(
        Integer,
        ForeignKey("product_definition.id"),
        nullable=False,
        comment='FK to product_definition.id table, extension product definition on shops domain'
    )
    shop_id = Column(Text, nullable=False, comment='Id Shop')
    product_url = Column(Text, nullable=False, comment='Product url')
    imp_catalog_page_id = Column(Integer, nullable=False, comment='Orginal images id')

    def __init__(self, product_definition_id, shop_id, product_url, imp_catalog_page_id):
        if product_definition_id is None:
            raise ValueError('Field product_definition_id can\'t be None')
        if shop_id is None:
            raise ValueError('Field shop_id can\'t be None')
        if product_url is None:
            raise ValueError('Field product_url can\'t be None')
        if imp_catalog_page_id is None:
            raise ValueError('Field imp_catalog_page_id can\'t be None')

        self.product_definition_id = product_definition_id
        self.shop_id = shop_id
        self.product_url = product_url
        self.imp_catalog_page_id = imp_catalog_page_id

    def __repr__(self):
        return '<ProductShop product_definition_id: {}, shop_id: {},  product_url: {}, imp_catalog_page_id: {}'.format(
            self.product_definition_id,
            self.shop_id,
            self.product_url,
            self.imp_catalog_page_id
        )


product_shop_shop_id_idx = Index(
    'product_shop_shop_id_idx',
    ProductShop.shop_id
)

product_shop_imp_catalog_page_id_idx = Index(
    'product_shop_imp_catalog_page_id_idx',
    ProductShop.imp_catalog_page_id
)


class ProductShopPrice(DbUtils):
    __tablename__ = 'product_shop_price'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_shop_id = Column(
        Integer,
        ForeignKey("product_shop.id"),
        nullable=False,
        comment='FK to product_shop.id table, extension product definition on price domain'
    )
    scan_date = Column(Date, nullable=False, comment='Scan date')
    price = Column(Float, nullable=False, comment='Product price')
    currency = Column(String, nullable=False, comment='Product price Currency')

    def __init__(self, product_shop_id, scan_date, price, currency):
        if product_shop_id is None:
            raise ValueError('Field product_shop_id can\'t be None')
        if scan_date is None:
            raise ValueError('Field scan_date can\'t be None')
        if price is None:
            raise ValueError('Field price can\'t be None')
        if currency is None:
            raise ValueError('Field price can\'t be None')

        self.product_shop_id = product_shop_id
        self.scan_date = scan_date
        self.price = price
        self.currency = currency

    def __repr__(self):
        return '<ProductShopPrice ProductShopID: {} ScanDate: {} Price: {}>'.format(
            self.product_shop_id,
            self.scan_date,
            self.price
        )


product_shop_price_scan_date_idx = Index(
    'product_shop_price_scan_date_idx',
    ProductShopPrice.scan_date
)


class ProductCategoryDef(DbUtils):
    __tablename__ = 'product_category_definition'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    name = Column(Text, nullable=False, comment='category name')
    meta_category_id = Column(Integer, nullable=False, comment='slack fk to meta category definition')

    def __init__(self, name, meta_category_id):
        if name is None or name == '':
            raise ValueError('Field name can\'t be empty')
        if meta_category_id is None:
            raise ValueError('Field meta_category_id can\'t be None')

        self.name = name
        self.meta_category_id = meta_category_id

    def __rapr__(self):
        return '<ProductCategoryDef name: {} meta_category_id: {}>'.format(self.name, self.meta_category_id)


product_category_definition_meta_category_id_idx = Index(
    'product_category_definition_meta_category_id_idx',
    ProductCategoryDef.meta_category_id
)


class ProductCategory(DbUtils):
    __tablename__ = 'product_category'
    __seqname__ = '{}_id_seq'.format(__tablename__)

    id = Column(Integer, Sequence(__seqname__), primary_key=True)
    product_definition_id = Column(
        Integer,
        ForeignKey("product_definition.id"),
        nullable=False,
        comment='FK to product_definition.id table'
    )
    product_category_id = Column(
        Integer,
        ForeignKey("product_category_definition.id"),
        nullable=False,
        comment='FK to product_category_definition.id table'
    )

    def __init__(self, product_definition_id, product_category_id):
        if product_definition_id is None:
            raise ValueError('Field product_definition_id can\'t be None')
        if product_category_id is None:
            raise ValueError('Field product_category_id can\'t be None')

        self.product_definition_id = product_definition_id
        self.product_category_id = product_category_id

    def __repr__(self):
        return '<ProductCategory product_definition_id: {}, product_category_id: {}'.format(
            self.product_definition_id,
            self.product_category_id
        )
