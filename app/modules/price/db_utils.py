from app import db
from sqlalchemy import and_, case
from sqlalchemy import cast, Date
from sqlalchemy.sql.expression import func
from app.modules.price.models import (EntryPoint, Shop, Category, Ofert, Brand, Product, KeyWord, KeyWordLink, MetaCategory, Image, ProductPrice, TagWordLink, ProductVersion, ProductShopUrl, ImageRepo, ProductImage, OfertArch, ProductStatement, TagProduct, Tag, TagProductDef, TagOfert, CategorySynonym) # noqa E501
from app.utils.url_utils import UrlUtils
from app.utils.local_type import TempProduct, MenuLink
from app.utils.db_transaction import commit_after_execution
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased

import logging
log = logging.getLogger(__name__)


class ProductVersionDbUtils():
    def add_product_version(self, product_id) -> int:
        pv = ProductVersion(product_id)
        db.session.add(pv)
        db.session.flush()
        return pv.id

    def search_product_by_tags(self, product_id, tag_id_list):
        result = db.session.query(
            func.count(ProductVersion.id).label('count'),
            ProductVersion.id.label('id')
        ).join(
            TagWordLink,
            TagWordLink.product_version_id == ProductVersion.id
        ).filter(
            and_(
                ProductVersion.product_id == product_id,
                TagWordLink.key_word_id.in_(tag_id_list)
            )
        ).group_by(
            ProductVersion.id
        ).first()
        return result

    def search_version_by_products_name(self, name, brand_id, category_id, url):
        result = db.session.query(
            ProductVersion.id.label('id')
        ).join(
            Product,
            and_(
                ProductVersion.product_id == Product.id,
                Product.active == True, # noqa E712
                Product.deleted == False
            )
        ).join(
            ProductShopUrl,
            and_(
                ProductShopUrl.product_version_id == ProductVersion.id,
                ProductShopUrl.url == url,
                ProductShopUrl.active == True, # noqa E712
                ProductShopUrl.deleted == False
            )
        ).join(
            TagWordLink,
            and_(
                TagWordLink.product_version_id == ProductVersion.id,
                TagWordLink.active == True, # noqa E712
                TagWordLink.deleted == False
            ),
            isouter = True
        ).filter(
            and_(
                Product.name == name,
                Product.brand_id == brand_id,
                Product.category_id == category_id,
                ProductVersion.active == True, # noqa E712
                ProductVersion.deleted == False,
                TagWordLink.id.is_(None)
            )
        ).first()
        return result

class EntryPointsDbUtils():
    def get_list_all_entry_points(self, enty_point_id=None):
        ep = EntryPoint
        if enty_point_id:
            result = db.session.query(
                ep.id,
                ep.url,
                Category.id
            ).join (
                Category,
                Category.id == ep.category_id
            ).filter(
                and_(
                    ep.active == True, # noqa E712
                    ep.deleted == False, # noqa E712
                    ep.id == enty_point_id
                )
            )
        else:
            result = db.session.query(
                ep.id,
                ep.url,
                Category.id
            ).join(
                Category,
                Category.id == ep.category_id
            ).filter(
                and_(
                    ep.active == True, # noqa E712
                    ep.deleted == False # noqa E712
                )
            )
        return result.all()
        """
        return [
            entity
            for entity in result
        ]
        """

    def is_entry_point_exists(self, url):
        return db.session.query(
            EntryPoint.id
        ).filter(
            EntryPoint.url == url
        ).first()

    def add_entry_point_with_check_shop(self, entry_point, category_id):
        entry_point_id = self.is_entry_point_exists(entry_point)
        if not entry_point_id:
            u = UrlUtils(entry_point)
            sdu = ShopDbUtils()
            shop_id = sdu.add_new_shop(u.domain)
            ep = EntryPoint(entry_point, category_id, shop_id)
            log.info('Added new entry point %r for category_id: %r,  shop_id: %r', entry_point,  category_id, shop_id)
            db.session.add(ep)
            db.session.commit()
        else:
            log.info('Entry point %r exist', entry_point)

    def add_list_enty_points_with_check_shop(self, list_entry_point, category_id):
        for entry_point in list_entry_point:
            self.add_enty_point_with_check_shop(entry_point, category_id)


class ShopDbUtils():
    def is_shop_exists(self, url: str):
        return db.session.query(
            Shop.id
        ).filter(
            Shop.url == url
        ).first()

    def add_new_shop(self, url) -> None:
        log.info('Add new shop domain %r', url)
        id_shop = self.is_shop_exists(url)
        if not id_shop:
            s = Shop(url)
            db.session.add(s)
            db.session.commit()
            log.info('save object s: %r', s.id)
            return s.id
        else:
            return id_shop


class OfertDbUtils():
    def get_all_ofert_by_category(self, category_id: int) -> list:
        return db.session.query(
            Ofert.id,
            Ofert.title,
            Ofert.entry_point_id,
            Category.name,
            Ofert.manufacturer
        ).join(
            EntryPoint,
            EntryPoint.id == Ofert.entry_point_id
        ).join(
            Category,
            Category.id == EntryPoint.category_id
        ).all()

    def get_all_ofert_by_entry_point(self, entry_point_id: int) -> list:
        return db.session.query(
            Ofert.id,
            Ofert.title,
            Ofert.entry_point_id,
            Category.name,
            Ofert.manufacturer,
            Ofert.creation_date
        ).join(
            EntryPoint,
            EntryPoint.id == Ofert.entry_point_id
        ).join(
            Category,
            Category.id == EntryPoint.category_id
        ).filter(
            EntryPoint.id == entry_point_id
        ).all()


    def get_all_brand_by_category(self, category_id: int) -> list:
        result = db.session.query(
            Ofert.manufacturer
        ).filter(
            and_(
                Ofert.manufacturer.isnot(None),
                Ofert.manufacturer != ''
            )
        ).group_by(
            Ofert.manufacturer
        ).all()
        return [
            ent[0].lower()
            for ent in result
        ]

    def get_all_oferts(self, ofert_id=None, shop_id=None, entry_point_id=None):
        o = db.session.query(
            Ofert.id,
            func.lower(Ofert.title).label('title'),
            Ofert.url,
            Ofert.image,
            Ofert.price,
            Ofert.currency,
            Ofert.manufacturer,
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            Shop.id.label('shop_id'),
            Shop.url.label('shop_url'),
            Image.control_sum,
            Ofert.creation_date.label('product_date'),
            Image.dimension,
            Image.size.label('img_size'),
            Image.orientation,
            Image.main_color,
            Shop.is_brand_shop,
            Image.size
        ).join(
            EntryPoint,
            EntryPoint.id == Ofert.entry_point_id
        ).join(
            Category,
            Category.id == EntryPoint.category_id
        ).join(
            Shop,
            Shop.id == EntryPoint.shop_id
        ).join(
            Image,
            Image.image == Ofert.image
        )

        o = o.filter(Ofert.creation_date.cast(Date) == func.current_date())

        if ofert_id:
            o = o.filter(Ofert.id == ofert_id)
        if shop_id:
            o = o.filter(Shop.id == shop_id)
        if entry_point_id:
            o.filter(Ofert.entry_point_id == entry_point_id)
        o = o.order_by(Shop.is_brand_shop.asc(), Ofert.manufacturer.asc())
        return o.all()


class BrandDbUtils():
    def new_brand(self, brand_name, logo=None):
        b = Brand(brand_name, logo)
        db.session.add(b)
        db.session.flush()
        return b.id

    @commit_after_execution
    def add_brand(self, brand_name, logo=None):
        brand_id =  self.is_brand_exists(brand_name)
        if brand_id:
            return brand_id
        else:
            brand_id = self.new_brand(brand_name, logo)
            return brand_id

    def get_all_brand(self):
        return db.session.query(
            Brand.id,
            Brand.name
        ).all()

    def get_all_brand_as_list(self):
        return [
            brands_tuple[1]
            for brands_tuple in self.get_all_brand()
        ]

    def is_brand_exists(self, name):
        return db.session.query(
            Brand.id
        ).filter(
            Brand.name == name
        ).first()

    def get_brand_id_by_name(self, name):
        """Synonym for method is_brand_exists"""
        return self.is_brand_exists(name)

    def get_brand_by_product_name(self, product_name):
        return db.session.query(
            Brand.id
        ).join(
            Product,
            and_(
                Product.brand_id == Brand.id,
                Product.active == True,
                Product.deleted == False,
                Product.name == product_name
            )
        ).filter(
            and_(
                Brand.active == True,
                Brand.deleted == False
            )
        ).first()


class ProductDbUtils():
    """
    def add_product(self, name, brand_id, category_id):
        p = Product(name, brand_id, category_id)
        db.session.add(p)
        db.session.commit()
    """

    def if_product_exists(self, name, brand_id, category_id):
        return db.session.query(
            Product.id
        ).filter(
            Product.name == name.lower(),
            Product.brand_id == brand_id,
            Product.category_id == category_id,
            Product.active == True, # noqa E712
            Product.deleted == False
        ).first()

    # @commit_after_execution
    def add_product(self, tp: TempProduct): # noqa F811
        bdbu = BrandDbUtils()
        log.info('Tp object %r', tp.get_dict())
        product_found = self.if_product_exists(tp.title.lower(), tp.brand_id, tp.category_id)
        if not product_found:
            p = Product(tp.title.lower(), tp.brand_id, tp.category_id, tp.slug)
            db.session.add(p)
            db.session.flush()
            return p.id
        else:
            log.warning('Product exists %r on ID = %r', tp.title.lower(), product_found.id)

    @commit_after_execution
    def save_product(self, tp_object):
        pvdbu = ProductVersionDbUtils()
        twldu = TagWordLinkDbUtils()
        
        if not tp_object.product_id:
            product_id = self.add_product(tp_object)
        else:
            product_id = tp_object.product_id

        if not tp_object.product_version_id:
            log.info('Create new product version for product ID={}'.format(product_id))
            product_version_id = pvdbu.add_product_version(product_id)
        else:
            product_version_id = tp_object.product_version_id

        log.info('To jest product version ID %r', product_version_id)
        if not tp_object.product_version_id and tp_object.tag:
            twldu.bulk_tag_binding(
                product_version_id,
                tp_object.tag
            )

        self.add_price_to_product(
            product_version_id,
            tp_object.shop_id,
            tp_object.price,
            tp_object.product_date
        )

        psudu = ProductShopUrlDbUtils()
        psudu.add_products_url(
            tp_object.url,
            product_version_id,
            tp_object.shop_id
        ) 
        irdu = ImageRepoDbUtils()
        repo_image_id = irdu.add_image_to_repo(
            tp_object.image,
            tp_object.control_sum,
            tp_object.dimension,
            tp_object.size,
            tp_object.orientation,
            tp_object.main_color
        )

        pidu = ProductImageDbUtils()
        pidu.add_products_image(
            product_version_id,
            repo_image_id
        )

        ps = ProductStatementDbUtils()
        # ps.add_statment(
        # )


    def add_price_to_product(self, product_id, shop_id, price, date_price):
        pp = ProductPrice(product_id, shop_id, price, date_price)
        db.session.add(pp)
        db.session.flush()

    def get_product_for_catgeory_view(self, category_id_):
        log.info('\n\n Jestem tutaj, szukam dla Category ID: %r', category_id_)
        product = db.session.query(
            TagProduct.tag_product_def_id.label('product_id'),
            func.string_agg(Tag.value, ' ').label('title')
        ).join(
            TagProduct,
            TagProduct.tag_id == Tag.id
        ).group_by(
            TagProduct.tag_product_def_id
        ).cte('product')

        max_date = db.session.query((func.max(Ofert.creation_date)).cast(Date))

        return db.session.query(
            product.c.product_id,
            product.c.title,
            func.max(Ofert.price).label('max_price'),
            func.min(Ofert.price).label('min_price'),
            func.count(Ofert.id).label('count'),
            func.max(Image.image).label('image')
        ).join(
            TagOfert,
            TagOfert.tag_product_def_id == product.c.product_id
        ).join(
            Ofert,
            Ofert.id == TagOfert.ofert_id
        ).join(
            Image,
            Image.image == Ofert.image
        ).join(
            TagProductDef,
            and_(
                TagProductDef.id == TagOfert.tag_product_def_id,
                TagProductDef.category_id == category_id_
            )
        ).filter(
            and_ (
                TagOfert.creation_date.cast(Date) == max_date, # func.current_date(),
                Ofert.creation_date.cast(Date) == max_date# func.current_date()
            )
        ).group_by(
            product.c.product_id,
            product.c.title
        ).order_by(
            desc(
                func.count(Ofert.id)
            )
        )
    

    def get_product_by_product_def_id(self, product_def_id):
        return db.session.query(
            TagOfert.tag_product_def_id.label('product_id'),
            Ofert.id.label('ofert_id'),
            Ofert.url,
            Ofert.title,
            Image.image,
            Ofert.price,
            Ofert.currency,
            Image.control_sum,
            Brand.name.label('brand_name'),
            func.string_agg(Tag.value, ';').label('tags')
        ).join(
            Ofert,
            Ofert.id == TagOfert.ofert_id
        ).join(
            Image,
            Image.image == Ofert.image
        ).join(
            TagProductDef,
            TagProductDef.id == TagOfert.tag_product_def_id,
        ).join(
            TagProduct,
            TagProduct.tag_product_def_id == TagProductDef.id
        ).join(
            Tag,
            Tag.id == TagProduct.tag_id,
            isouter = True
        ).join(
            Brand,
            Brand.id == TagProductDef.brand_id,
            isouter = True
        ).filter(
            and_(
                TagOfert.tag_product_def_id == product_def_id,
                TagOfert.creation_date.cast(Date) == func.current_date()
            )
        ).group_by(
            TagOfert.tag_product_def_id,
            Ofert.id,
            Ofert.url,
            Ofert.title,
            Image.image,
            Ofert.price,
            Ofert.currency,
            Image.control_sum,
            Brand.name
        ).order_by(
            asc(Ofert.price)
        ).all()

class ProductStatementDbUtils():
    def add_statment(self, ofert_arch_id, brand_id, category_id, product_id, poduct_version_id, shop_id, product_image_id, product_shop_url_id, product_price_id):
        ps = ProductStatement(ofert_arch_id, brand_id, category_id, product_id, poduct_version_id, shop_id, product_image_id, product_shop_url_id, product_price_id)
        db.session.add(pp)
        db.session.flush()


class OfertArchDbUtils():
    def add_arch_ofert(self, last_id, entry_point_id, title, price, currency, url, image, manufacturer):
        oa = OfertArch(last_id, entry_point_id, title, price, currency, url, image, manufacturer)
        db.session.add(oa)
        db.session.flush()


class KeyWordDbUtils():
    def add_word(self, word):
        k = KeyWord(word)
        db.session.add(k)
        db.session.flush()
        return k.id

    def if_word_exists(self, word):
        return db.session.query(
            KeyWord.id
        ).filter(
            KeyWord.value == word
        ).first()


class KeyWordLinkDbUtils():
    
    @commit_after_execution
    def add_word_to_category(self, category_id, word):
        kwdu = KeyWordDbUtils()
        key_word_id = kwdu.if_word_exists(word)
        if not key_word_id:
            key_word_id = kwdu.add_word(word)
        kwl = KeyWordLink(category_id, key_word_id)
        db.session.add(kwl)
        db.session.flush()
        return kwl.id

    def get_all_word(self):
        return db.session.query(
            KeyWord.value,
            KeyWordLink.category_id,
            KeyWord.id
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id
        ).all()

    def get_word_by_category(self, category_id):
        words = db.session.query(
            KeyWord.value
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id
        ).filter(
            KeyWordLink.category_id == category_id
        ).all()
        return [
            word[0]
            for word in words
        ]


class CategoryDbUtils():
    def add_category(self, name, meta_category_id):
        catgeory = Category(name, meta_category_id)
        db.session.add(catgeory)
        db.session.commit()
        return catgeory.id

    def get_all_category(self):
        return db.session.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            MetaCategory.id.label('metacategory_id'),
            MetaCategory.name.label('meta_category_name')
        ).join(
            MetaCategory,
            MetaCategory.id == Category.meta_category_id
        ).all()

    def get_category_for_menu(self):
        result = db.session.query(
            Category.name.label('category_name'),
            Category.slug.label('category_slug'),
            MetaCategory.name.label('meta_category_name')
        ).join(
            MetaCategory,
            MetaCategory.id == Category.meta_category_id
        ).filter(
            Category.active == True,
            Category.deleted == False,
            MetaCategory.active == True,
            MetaCategory.deleted == False
        ).all()
        return [
            MenuLink(
                entiti.category_name,
                entiti.category_slug,
                entiti.meta_category_name
            )
            for entiti in result
        ]

    def get_category_name_by_id(self, category_id):
        catgeory = db.session.query(
            Category.name
        ).filter(
            Category.id == category_id
        ).first()
        return catgeory[0]


    def get_category_id_by_slug(self, category_slug):
        return db.session.query(
            Category.id
        ).filter(
            Category.slug == category_slug
        ).first()


class TagWordLinkDbUtils():

    @commit_after_execution
    def add_tag(self, name, product_id):
        kwdu = KeyWordDbUtils()
        result = kwdu.if_word_exists(name)
        if result:
            word_id = result
        else:
            word_id = kwdu.add_word(name)
        twl = TagWordLink(product_id, word_id)
        db.session.add(twl)
        db.session.flush()
        return twl.id

    @commit_after_execution
    def add_loose_tag(self, name):
        kwdu = KeyWordDbUtils()
        result = kwdu.if_word_exists(name)
        if result:
            word_id = result
        else:
            word_id = kwdu.add_word(name)
        return word_id

    def get_tags(self):
        return db.session.query(
            KeyWord.id,
            KeyWord.value
        ).join(
            KeyWordLink,
            KeyWordLink.key_word_id == KeyWord.id,
            isouter=True
        ).filter(
            KeyWordLink.id.is_(None)
        ).all()

    def binding_tag(self, product_version_id, word_id):
        twl = TagWordLink(product_version_id, word_id)
        db.session.add(twl)
        db.session.flush()
        return twl.id

    def bulk_tag_binding(self, product_version_id, tag_list):
        """
        param: product_version_id (int): 
        param: tag_list: (id_word, word)
        """
        list_added_tag = []
        for word_id, word in tag_list:
            id = self.binding_tag(product_version_id, word_id)
            list_added_tag.append(id)
        return list_added_tag


class ProductShopUrlDbUtils():

    def add_products_url(self, url, product_version_id, shop_id):
        products_shop_url = self.if_products_utl_exists(url, product_version_id, shop_id)
        if products_shop_url:
            return products_shop_url
        else:
            psu = ProductShopUrl(url, product_version_id, shop_id)
            db.session.add(psu)
            db.session.flush()
            return psu.id

    def if_products_utl_exists(self, url, product_version_id, shop_id):
        return db.session.query(
            ProductShopUrl.id
        ).filter(
            ProductShopUrl.url == url,
            ProductShopUrl.product_version_id == product_version_id,
            ProductShopUrl.shop_id == shop_id
        ).first()


class ImageRepoDbUtils():

    def add_image_to_repo(self, image, control_sum, dimension, size, orientation, main_color):
        img = self.if_image_exists_in_repo(image)
        if img:
            return img
        else:
            ir = ImageRepo(image, control_sum)
            ir.dimension = dimension
            ir.size = size
            ir.orientation = orientation
            ir.main_color = main_color
            db.session.add(ir)
            db.session.flush()
            return ir.id

    def if_image_exists_in_repo(self, image):
        return db.session.query(
            ImageRepo.id
        ).filter(
            ImageRepo.image == image
        ).first()

class ProductImageDbUtils():

    def add_products_image(self, product_version_id, repo_image_id):
            product_images_id = self.if_products_image_exists(product_version_id, repo_image_id)
            if product_images_id:
                return product_images_id
            else:
                pi = ProductImage(product_version_id, repo_image_id)
                db.session.add(pi)
                db.session.flush()
                return pi.id

    def if_products_image_exists(self, product_version_id, repo_image_id):
        return db.session.query(
            ProductImage.id
        ).filter(
            ProductImage.product_version_id == product_version_id,
            ProductImage.repo_image_id == repo_image_id
        ).first()


class TagDbUtils():
    def add_tag(self, word):
        k = Tag(word)
        db.session.add(k)
        db.session.flush()
        return k.id

    def save_tag(self, tag):
        tag_id = self.if_tag_exists(tag)
        if tag_id:
            return tag_id
        else:
            return self.add_tag(tag)

    def if_tag_exists(self, word):
        return db.session.query(
            Tag.id
        ).filter(
            Tag.value == word
        ).first()

    def bulk_save_tag(self, tags_list):
        return [
            (
                self.save_tag(tag),
                tag
            )
            for tag in tags_list
        ]
    
    @commit_after_execution
    def c_bulk_save_tag(self, tags_list):
        return self.bulk_save_tag(tags_list)

    #def get_bulk_tags(self, tags_list):
    def get_bulk_tags(self, strings_tags):
        """
        :param strings_tags tags delimeter by ; symbol
        """


        a = db.session.query(func.unnest(func.string_to_array(strings_tags, ';')).label('tag')).cte('a')
        b = db.session.query(Tag.id, a.c.tag, Tag.meaning  ).join(Tag, a.c.tag == Tag.value, isouter = True).cte('b')
        return db.session.query(b.c.id.label('tag_id'), b.c.tag, b.c.meaning).all()

class TagProductDbUtils():

    def get_tags_by_product(self, tag_product_def_id):
        pass

    # def get_product_by_tags_list(self, strings_tags, category_id, brand_id):
    def get_product_by_tags_list(self, tags_list, category_id, brand_id):
        base_query = db.session.query(
            TagProductDef.id
        ).join(
            TagProduct,
            TagProduct.tag_product_def_id == TagProductDef.id
        ).filter(
            and_(
                TagProductDef.category_id == category_id,
                TagProductDef.brand_id == brand_id,
                TagProduct.active == True,
                TagProduct.deleted == False,
                TagProductDef.active == True,
                TagProductDef.deleted == False
            )
        )

        list_tag_alias = []
        for tag in tags_list:
            tag_alias = aliased(Tag)
            base_query = base_query.join(
                tag_alias,
                and_(
                    tag_alias.id == TagProduct.tag_id,
                    tag_alias.value == tag
                ),
                isouter = True
            )
            list_tag_alias.append(tag_alias)

        base_query = base_query.group_by(TagProductDef.id)


        for alias in list_tag_alias:
            base_query = base_query.having(
                func.max(alias.value).isnot(None)
            )

        return base_query.first()

        """ V. 3
        search_tags = db.session.query(
            func.unnest(
                func.string_to_array(
                    strings_tags,
                    ';'
                )
            ).label(
                'tag'
            )
        ).cte('search_tags')

        gaps = db.session.query(
            Tag.id,
            Tag.meaning,
            search_tags.c.tag
        ).join(
            Tag,
            Tag.value == search_tags.c.tag,
            isouter = True
        ).filter(
            Tag.id.isnot(None)
        ).cte('gaps')

        return db.session.query(
            TagProduct.tag_product_def_id.label('product_id')
        ).select_from(
            gaps
        ).join(
            TagProduct,
            TagProduct.tag_id == gaps.c.id,
            isouter = True
        ).join(
            TagProductDef,
            and_(
                TagProduct.tag_product_def_id == TagProductDef.id,
                TagProductDef.category_id == category_id,
                TagProductDef.brand_id == brand_id
            )
        ).filter(
            gaps.c.meaning.is_(None)
        ).all()
        """

        """ V. 2
        a = db.session.query(
            func.unnest(
                func.string_to_array(
                    strings_tags,
                    ';'
                )
            ).label(
                'tag'
            )
        ).cte('a')

        prd = db.session.query(
            func.min(
                case(
                    [
                        (
                            TagProduct.tag_product_def_id.is_(None),
                            0
                        )
                    ],
                    else_=TagProduct.tag_product_def_id
                )
            ).label('prod_id')
        ).select_from(
            a
        ).join(
            Tag,
            Tag.value == a.c.tag,
        ).join(
            TagProduct,
            TagProduct.tag_id == Tag.id,
            isouter = True
        ).cte('prd')
        
        return db.session.query(
            prd.c.prod_id
        ).filter(
            prd.c.prod_id > 0
        ).all()
        """

        """ V.1 
        return db.session.query(
            TagProduct.tag_product_def_id
        ).join(
            Tag,
            Tag.id == TagProduct.tag_id,
            isouter = True
        ).filter(
            and_(
                TagProduct.active == True,
                TagProduct.deleted == False,
                Tag.active == True,
                Tag.deleted == False,
                Tag.value.in_(tags_list)
            )
        ).group_by(
            TagProduct.tag_product_def_id
        ).having(          
            func.min(
                case(
                    [
                        (
                            Tag.id.isnot(None),
                            1
                        )
                    ],
                    else_=0
                )
            ) == 1 
        ).all()
        """
    
    def bind_product_def_tag(self, tag_product_def_id, tag_id):
        tp = TagProduct(tag_product_def_id, tag_id)
        db.session.add(tp)
        db.session.flush()
        return tp.id

    def bulk_binding_product_tag(self, tag_product_def_id, tuples_tag_list):
        return [
            self.bind_product_def_tag(tag_product_def_id, tuple_tag[0]) 
            for tuple_tag in tuples_tag_list
        ]

    def add_tag_to_product(self, tags_list,  brand_id, category_id, product_def_id=None):
        tpdbu = TagProductDefDbUtils()
        tdbu = TagDbUtils()
        if not product_def_id:
            product_def_id = tpdbu.add_product_def(brand_id, category_id)
        tuples_tag_list = tdbu.bulk_save_tag(tags_list)
        return (
            product_def_id,
            self.bulk_binding_product_tag(product_def_id, tuples_tag_list)
        )

    @commit_after_execution
    def c_add_tag_to_product(self, tags_list,  brand_id, category_id, product_def_id=None):
        return self.add_tag_to_product(tags_list, brand_id, category_id, product_def_id)


class TagProductDefDbUtils():

    def add_product_def(self, brand_id, category_id):
        tpd = TagProductDef(category_id, brand_id)
        db.session.add(tpd)
        db.session.flush()
        return tpd.id

    @commit_after_execution
    def save_product_def(self, brand_id, category_id):
        return self.add_product_def(brand_id, category_id)

    def if_exists(self, product_def_id):
        return db.session.query(
            TagProductDef.id
        ).filter(
            and_(
                TagProductDef.id == product_def_id,
                TagProductDef.active == True,
                TagProductDef.deleted == False
            )
        ).first()

class TagOfertDbUtils():
    def add_ofert_to_product(self, ofert_id, product_def_id):
        to = TagOfert(ofert_id, product_def_id)
        db.session.add(to)
        db.session.flush()
        return to.id

    def save_ofert_to_product(self, ofert_id, product_def_id):
        to_id = self.if_exists(ofert_id, product_def_id)
        if to_id:
            return to_id
        else:
            return self.add_ofert_to_product(ofert_id, product_def_id)

    @commit_after_execution
    def c_save_ofert_to_product(self, ofert_id, product_def_id):
        return self.save_ofert_to_product(ofert_id, product_def_id)

    def if_exists(self, ofert_id, product_def_id):
        return db.session.query(
            TagOfert.id
        ).filter(
            and_(
                TagOfert.ofert_id == ofert_id,
                TagOfert.tag_product_def_id == product_def_id,
                TagOfert.active == True,
                TagOfert.deleted == False
            )
        ).first()

    def get_ofert_by_product(self, product_def_id):
        return db.session.query(
            Ofert.id
        )

    def register_product_by_tags(self, tags_list, ofert_id, brand_id, category_id):
        tpdbu = TagProductDbUtils()
        added = tpdbu.add_tag_to_product(tags_list, brand_id, category_id)
        return self.save_ofert_to_product(ofert_id, added[0])

    @commit_after_execution
    def c_register_product_by_tags(self, tags_list, ofert_id, brand_id, category_id):
        return self.register_product_by_tags(tags_list, ofert_id, brand_id, category_id)


class CategorySynonymDbUtils():

    def is_exists_synonym(self, category_id, value):
        return db.session.query(
            CategorySynonym.id
        ).filter(
            and_(
                CategorySynonym.category_id == category_id,
                CategorySynonym.value == value,
                CategorySynonym.active == True,
                CategorySynonym.deleted == False
            )
        ).first()


    def add_new_synonym(self, category_id, value):
        synonym_id = self.is_exists_synonym(category_id, value)
        if synonym_id:
            return synonym_id
        else:
            cs = CategorySynonym(category_id, value)
            db.session.add(cs)
            db.session.flush()
            return cs.id
 
    @commit_after_execution
    def c_add_new_synonym(self, category_id, value):
        return self.add_new_synonym(category_id, value)


    def get_category_id_by_synonym(self, value):
        return db.session.query(
            CategorySynonym.category_id
        ).filter(
            and_(
                CategorySynonym.value == value,
                CategorySynonym.active == True,
                CategorySynonym.deleted == False
            )
        ).first()

    def get_all_synonym(slef):
        return db.session.query(
            CategorySynonym.category_id,
            CategorySynonym.value
        ).filter(
            and_(
                CategorySynonym.active == True,
                CategorySynonym.deleted == False
            )
        ).all()

