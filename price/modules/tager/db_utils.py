import datetime
from price import db
from sqlalchemy import and_, or_
from sqlalchemy import desc
from sqlalchemy.sql.expression import func
from price.utils.db_transaction import commit_after_execution

from price.modules.tager.models import (
    TagerContext,
    TagerTag,
    TagerTagSynonym,
    TagerCategory,
    TagerCategorySynonym,
    TagerBrand,
    TagerBrandSynonym,
    TagerSize,
    TagerBrandAssignment,
    TagerCategoryAssignment,
    TagerColor,
    TagerColorSynonym,
    TagerTaggingResult,
)

import logging
log = logging.getLogger(__name__)


class TagerContextDbu():

    def get_all_context(self):
        return db.session.query(
            TagerContext.id,
            TagerContext.name
        ).all()

    def get_context_by_name(self, context):
        return db.session.query(
            TagerContext.id
        ).filter(
            and_(
                TagerContext.name == context,
                TagerContext.active.is_(True)
            )
        ).first()

    def get_context_by_id(self, context_id):
        return db.session.query(
            TagerContext.name
        ).filter(
            and_(
                TagerContext.id == context_id,
                TagerContext.active.is_(True)
            )
        ).all()

    def is_exists(self, context):
        context_id = self.get_context_by_name(context)
        if context_id:
            return context_id
        return None

    def add_context(self, context):
        context_id = self.is_exists(context)
        if not context_id:
            c = TagerContext(context)
            db.session.add(c)
            db.session.flush()
            context_id = c.id
        return context_id

    @commit_after_execution
    def c_add_context(self, context):
        return self.add_context(context)


class TagerBrandAssignmentDbu():

    def get_assignment(self, imp_catalog_page):
        return db.session.query(
            TagerBrandAssignment.id,
            TagerBrandAssignment.imp_catalog_page_id,
            TagerBrandAssignment.brand,
            TagerBrandAssignment.tager_brand_id
        ).filter(
            and_(
                TagerBrandAssignment.imp_catalog_page_id == imp_catalog_page,
                TagerBrandAssignment.active.is_(True)
            )
        ).first()

    def is_exists(self, imp_catalog_page):
        tager_brand_assignment_id = self.get_assignment(imp_catalog_page)
        if tager_brand_assignment_id:
            return tager_brand_assignment_id
        return None

    def add_assignment(self, imp_catalog_page_id, brand, tager_brand_id):
        log.info('Run add_assigment %r %r %r ', imp_catalog_page_id, brand, tager_brand_id)
        tager_brand_assignment = self.is_exists(imp_catalog_page_id)
        log.info('Found brand assigment %r', tager_brand_assignment)
        if not tager_brand_assignment:
            tba = TagerBrandAssignment(imp_catalog_page_id, brand, tager_brand_id)
            db.session.add(tba)
            db.session.flush()
            tager_brand_assignment = tba
        else:
            log.info('Change assigment {} old: {} -> new: {}'.format(
                tager_brand_assignment.imp_catalog_page_id,
                tager_brand_assignment.brand, brand
            ))
            t = TagerBrandAssignment.query.filter(
                TagerBrandAssignment.id == tager_brand_assignment.id
            ).first()
            tager_brand_assignment = t
            t.brand = brand
            t.tager_brand_id = tager_brand_id
            t.last_update_date = datetime.datetime.now()
            t.last_update_by = 1
            db.session.flush()
        return tager_brand_assignment.id

    @commit_after_execution
    def c_add_assignment(self, imp_catalog_page_id, brand, tager_brand_id):
        log.info('Save brand {} {}'.format(imp_catalog_page_id, brand))
        return self.add_assignment(imp_catalog_page_id, brand, tager_brand_id)


class TagerBrandDbu():
    def __all(self):
        return db.session.query(
            TagerBrand.id,
            TagerBrand.name
        ).filter(
            TagerBrand.active.is_(True)
        )

    def get_all(self):
        return self.__all().all()

    def get_id_by_name(self, name):
        return db.session.query(
            TagerBrand.id
        ).filter(
            and_(
                TagerBrand.name == name,
                TagerBrand.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, name):
        brand_id = self.get_id_by_name(name)
        if brand_id:
            return brand_id
        return None

    def add_brand(self, name):
        brand_id = self.is_exists(name)
        if not brand_id:
            tb = TagerBrand(name)
            db.session.add(tb)
            db.session.flush()
            brand_id = tb.id
        return brand_id

    @commit_after_execution
    def c_add_brand(self, name):
        return self.add_brand(name)


class TagerBrandSynonymDbu():

    def search_brnad(self, dict_tagging_product):
        imp_catalog_page_id = db.bindparam('imp_catalog_page_id', dict_tagging_product.get('imp_catalog_page_id'))
        catalog_url = db.bindparam('catalog_url', dict_tagging_product.get('catalog_url'))
        catalog_title = db.bindparam('catalog_title', dict_tagging_product.get('catalog_title'))
        catalog_img = db.bindparam('catalog_img', dict_tagging_product.get('catalog_img'))
        product_title = db.bindparam('product_title', dict_tagging_product.get('product_title'))

        fields = db.session.query(
            imp_catalog_page_id.label('imp_catalog_page_id'),
            func.lower(catalog_url).label('catalog_url'),
            func.lower(catalog_title).label('catalog_title'),
            func.lower(catalog_img).label('catalog_img'),
            func.lower(product_title).label('product_title'),
        ).cte('fields')

        result = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerBrand.name.label('value'),
            func.length(TagerBrandSynonym.value).label('string_len'),
            TagerBrandSynonym.tager_brand_id
        ).join(
            TagerBrandSynonym,
            and_(
                TagerBrandSynonym.active.is_(True),
                or_(
                    func.strpos(
                        func.lower(fields.c.catalog_url),
                        func.lower(TagerBrandSynonym.value)
                    ) > 0,
                    func.strpos(
                        func.lower(fields.c.catalog_title),
                        func.lower(TagerBrandSynonym.value)
                    ) > 0,
                    func.strpos(
                        func.lower(fields.c.catalog_img),
                        func.lower(TagerBrandSynonym.value)
                    ) > 0,
                    func.strpos(
                        func.lower(fields.c.product_title),
                        func.lower(TagerBrandSynonym.value)
                    ) > 0,
                )
            ),
            isouter=True
        ).join(
            TagerBrand,
            TagerBrand.id == TagerBrandSynonym.tager_brand_id,
            isouter=True
        ).cte('result')

        return db.session.query(
            result.c.imp_catalog_page_id,
            result.c.value.label('brand'),
            result.c.tager_brand_id
        ).order_by(
            desc(result.c.string_len)
        ).first()

    @commit_after_execution
    def c_add_brnad(self, name):
        tb = TagerBrandDbu()
        brand_id = tb.add_brand(name)
        brand_synonym_id = self.add_brand_synonym(brand_id, name)
        return brand_synonym_id

    @commit_after_execution
    def c_bulk_add_brnad(self, list_brands):
        tb = TagerBrandDbu()
        brand_id = tb.add_brand(list_brands[0])
        for name in list_brands:
            brand_synonym_id = self.add_brand_synonym(brand_id, name)
            log.info('Add synonym {}: ID: {}'.format(name, brand_synonym_id))
        return brand_id

    def get_id_by_name(self, value):
        return db.session.query(
            TagerBrandSynonym.id
        ).filter(
            and_(
                TagerBrandSynonym.value == value,
                TagerBrandSynonym.active.is_(True)
            )
        ).one_or_none()

    def get_brand_id_by_synonym_name(self, value):
        return db.session.query(
            TagerBrand.id
        ).join(
            TagerBrandSynonym,
            TagerBrandSynonym.tager_brand_id == TagerBrand.id
        ).filter(
            and_(
                TagerBrandSynonym.active.is_(True),
                TagerBrandSynonym.value == value,
                TagerBrand.active.is_(True)
            )
        ).first()

    def is_exists(self, value):
        brand_synonym_id = self.get_id_by_name(value)
        if brand_synonym_id:
            return brand_synonym_id
        return None

    def add_brand_synonym(self, brand_id, value):
        brand_synonym_id = self.is_exists(value)
        if not brand_synonym_id:
            tbs = TagerBrandSynonym(brand_id, value)
            db.session.add(tbs)
            db.session.flush()
            brand_synonym_id = tbs.id
        return brand_synonym_id

    @commit_after_execution
    def c_add_brand_synonym(self, brand_id, value):
        return self.add_brand(brand_id, value)


class TagerCategoryDbu():
    def get_id_by_name(self, name):
        return db.session.query(
            TagerCategory.id
        ).filter(
            and_(
                TagerCategory.name == name,
                TagerCategory.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, name):
        category_id = self.get_id_by_name(name)
        if category_id:
            return category_id
        return None

    def add_category(self, name):
        category_id = self.is_exists(name)
        if not category_id:
            tb = TagerCategory(name)
            db.session.add(tb)
            db.session.flush()
            category_id = tb.id
        return category_id

    @commit_after_execution
    def c_add_category(self, name):
        return self.add_category(name)


class TagerCategorySynonymDbu():

    def search_category(self, dict_tagging_product):
        imp_catalog_page_id = db.bindparam('imp_catalog_page_id', dict_tagging_product.get('imp_catalog_page_id'))
        catalog_url = db.bindparam('catalog_url', dict_tagging_product.get('catalog_url'))
        catalog_title = db.bindparam('catalog_title', dict_tagging_product.get('catalog_title'))
        catalog_img = db.bindparam('catalog_img', dict_tagging_product.get('catalog_img'))
        product_title = db.bindparam('product_title', dict_tagging_product.get('product_title'))
        product_desc = db.bindparam('product_desc', dict_tagging_product.get('product_desc'))
        product_path = db.bindparam('product_path', dict_tagging_product.get('product_path'))

        fields = db.session.query(
            imp_catalog_page_id.label('imp_catalog_page_id'),
            func.lower(catalog_url).label('catalog_url'),
            func.lower(catalog_title).label('catalog_title'),
            func.lower(catalog_img).label('catalog_img'),
            func.lower(product_title).label('product_title'),
            func.lower(product_desc).label('product_desc'),
            func.lower(product_path).label('product_path'),
        ).cte('fields')

        q1 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.catalog_url),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        q2 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.catalog_title),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        q3 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.catalog_img),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        q4 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.product_title),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        q5 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.product_desc),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        q6 = db.session.query(
            fields.c.imp_catalog_page_id,
            TagerCategorySynonym.tager_category_id,
            TagerCategorySynonym.value
        ).join(
            TagerCategorySynonym,
            and_(
                TagerCategorySynonym.active.is_(True),
                func.strpos(
                    func.lower(fields.c.product_path),
                    func.lower(TagerCategorySynonym.value)
                ) > 0,
            ),
            isouter=True
        )

        # result = q1.union(q2).union(q3).union(q4).union(q5).union(q6)
        qu = q1.union(q2, q2, q3, q4, q5, q6).subquery()

        result = db.session.query(
            TagerCategory.id,
            TagerCategory.name,
            func.count(TagerCategory.id).label('rate')
        ).join(
            qu,
            qu.c.tager_category_synonym_tager_category_id == TagerCategory.id
        ).group_by(
            TagerCategory.id,
            TagerCategory.name
        ).order_by(
            func.count(TagerCategory.id).desc()
        )

        return result.all()

    @commit_after_execution
    def c_add_category(self, name):
        tb = TagerCategoryDbu()
        category_id = tb.add_category(name)
        category_synonym_id = self.add_category_synonym(category_id, name)
        return category_synonym_id

    @commit_after_execution
    def c_bulk_add_category(self, list_categorys):
        tb = TagerCategoryDbu()
        category_id = tb.add_category(list_categorys[0])
        for name in list_categorys:
            category_synonym_id = self.add_category_synonym(category_id, name)
            log.info('Add synonym {}: ID: {}'.format(name, category_synonym_id))
        return category_id

    def get_id_by_name(self, value):
        return db.session.query(
            TagerCategorySynonym.id
        ).filter(
            and_(
                TagerCategorySynonym.value == value,
                TagerCategorySynonym.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, value):
        category_synonym_id = self.get_id_by_name(value)
        if category_synonym_id:
            return category_synonym_id
        return None

    def add_category_synonym(self, category_id, value):
        category_synonym_id = self.is_exists(value)
        if not category_synonym_id:
            tbs = TagerCategorySynonym(category_id, value)
            db.session.add(tbs)
            db.session.flush()
            category_synonym_id = tbs.id
        return category_synonym_id

    @commit_after_execution
    def c_add_category_synonym(self, category_id, value):
        return self.add_category(category_id, value)


class TagerCategoryAssignmentDbu():
    def get_assignment(self, imp_catalog_page, category):
        return db.session.query(
            TagerCategoryAssignment.id,
            TagerCategoryAssignment.imp_catalog_page_id,
            TagerCategoryAssignment.category
        ).filter(
            and_(
                TagerCategoryAssignment.imp_catalog_page_id == imp_catalog_page,
                TagerCategoryAssignment.category == category,
                TagerCategoryAssignment.active.is_(True)
            )
        ).first()

    def get_category_assignment(self, imp_catalog_page):
        return db.session.query(
            TagerCategoryAssignment.id,
            TagerCategoryAssignment.imp_catalog_page_id,
            TagerCategoryAssignment.category,
            TagerCategoryAssignment.rate
        ).join(
            TagerCategory,
            TagerCategoryAssignment.category == TagerCategory.name
        ).filter(
            and_(
                TagerCategoryAssignment.imp_catalog_page_id == imp_catalog_page,
                TagerCategoryAssignment.active.is_(True),
                TagerCategory.active.is_(True)
            )
        ).all()

    def is_exists(self, imp_catalog_page, category):
        tager_category_assignment_id = self.get_assignment(imp_catalog_page, category)
        if tager_category_assignment_id:
            return tager_category_assignment_id
        return None

    def add_assignment(self, imp_catalog_page_id, category, rate):
        tager_category_assignment = self.is_exists(imp_catalog_page_id, category)
        if not tager_category_assignment:
            tca = TagerCategoryAssignment(imp_catalog_page_id, category, rate)
            db.session.add(tca)
            tager_category_assignment = tca
        else:
            log.info('Change assigment {} old: {} -> new: {}'.format(
                tager_category_assignment.imp_catalog_page_id,
                tager_category_assignment.category,
                category
                )
            )
            t = TagerCategoryAssignment.query.filter(
                TagerCategoryAssignment.id == tager_category_assignment.id
            ).first()
            t.category = category
            t.rate = rate
            t.last_update_date = datetime.datetime.now()
            t.last_update_by = 1
        db.session.flush()
        return tager_category_assignment.id

    @commit_after_execution
    def c_add_assignment(self, imp_catalog_page_id, category, rate):
        # log.info('Dodaje wpis {} {} #{}'.format(imp_catalog_page_id, category, rate))
        return self.add_assignment(imp_catalog_page_id, category, rate)


class TagerColorDbu():
    def get_id_by_name(self, name):
        return db.session.query(
            TagerColor.id
        ).filter(
            and_(
                TagerColor.name == name,
                TagerColor.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, name):
        color_id = self.get_id_by_name(name)
        if color_id:
            return color_id
        return None

    def add_color(self, name):
        color_id = self.is_exists(name)
        if not color_id:
            tb = TagerColor(name)
            db.session.add(tb)
            db.session.flush()
            color_id = tb.id
        return color_id

    @commit_after_execution
    def c_add_color(self, name):
        return self.add_color(name)


class TagerColorSynonymDbu():

    @commit_after_execution
    def c_add_color(self, name):
        tb = TagerColorDbu()
        color_id = tb.add_color(name)
        color_synonym_id = self.add_color_synonym(color_id, name)
        return color_synonym_id

    @commit_after_execution
    def c_bulk_add_color(self, list_colors):
        tb = TagerColorDbu()
        color_id = self.get_similarity(list_colors[0])
        if not color_id:
            color_id = tb.add_color(list_colors[0])
        for name in list_colors:
            color_synonym_id = self.add_color_synonym(color_id, name)
            log.info('Add synonym {}: ID: {}'.format(name, color_synonym_id))
        return color_id

    def get_id_by_name(self, value):
        return db.session.query(
            TagerColorSynonym.id
        ).filter(
            and_(
                TagerColorSynonym.value == value,
                TagerColorSynonym.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, value):
        color_synonym_id = self.get_id_by_name(value)
        if color_synonym_id:
            return color_synonym_id
        return None

    def get_similarity(self, value):
        return db.session.query(
            TagerColor.id
            # TagerColor.name
        ).filter(
            func.similarity(
                TagerColor.name, value
            ) > 0.3
        ).first()

    def add_color_synonym(self, color_id, value):
        color_synonym_id = self.is_exists(value)
        if not color_synonym_id:
            tbs = TagerColorSynonym(color_id, value)
            db.session.add(tbs)
            db.session.flush()
            color_synonym_id = tbs.id
        return color_synonym_id

    @commit_after_execution
    def c_add_color_synonym(self, brand_id, value):
        return self.add_brand(brand_id, value)


class TagerTagDbu():
    def get_id_by_name(self, name):
        return db.session.query(
            TagerTag.id
        ).filter(
            and_(
                TagerTag.value == name,
                TagerTag.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, name):
        tag_id = self.get_id_by_name(name)
        if tag_id:
            return tag_id
        return None

    def add_tag(self, tager_context_id, name):
        tag_id = self.is_exists(name)
        if not tag_id:
            tt = TagerTag(tager_context_id, name)
            db.session.add(tt)
            db.session.flush()
            tag_id = tt.id
        return tag_id

    @commit_after_execution
    def c_add_tag(self, tager_context_id, name):
        return self.add_tag(tager_context_id, name)


class TagerTagSynonymDbu():

    @commit_after_execution
    def c_add_tag(self, tager_context_id, name):
        tt = TagerTagDbu()
        tag_id = tt.add_tag(tager_context_id, name)
        tag_synonym_id = self.add_tag_synonym(tag_id, name)
        return tag_synonym_id

    @commit_after_execution
    def c_bulk_add_tag(self, tager_context_id, list_tags):
        tt = TagerTagDbu()
        tag_id = self.get_similarity(list_tags[0])
        if not tag_id:
            log.info('"Save tag: "{}" context_id: "{}"'.format(list_tags[0], tager_context_id))
            tag_id = tt.add_tag(tager_context_id, list_tags[0])
        for name in list_tags:
            tag_synonym_id = self.add_tag_synonym(tag_id, name)
            log.info('Add synonym "{}", TagID: "{}" TagSynonymID "{}"'.format(name, tag_id, tag_synonym_id))
        return tag_id

    def get_id_by_name(self, value):
        return db.session.query(
            TagerTagSynonym.id
        ).filter(
            and_(
                TagerTagSynonym.value == value,
                TagerTagSynonym.active.is_(True)
            )
        ).one_or_none()

    def is_exists(self, value):
        tag_synonym_id = self.get_id_by_name(value)
        if tag_synonym_id:
            return tag_synonym_id
        return None

    def get_similarity(self, value):
        return db.session.query(
            TagerTag.id
        ).filter(
            func.similarity(
                TagerTag.value, value
            ) > 0.3
        ).first()

    def add_tag_synonym(self, tag_id, value):
        tag_synonym_id = self.is_exists(value)
        if not tag_synonym_id:
            log.info('Save new tag: {} tag_id: {}'.format(value, tag_id))
            tts = TagerTagSynonym(tag_id, value)
            db.session.add(tts)
            db.session.flush()
            tag_synonym_id = tts.id
        return tag_synonym_id

    @commit_after_execution
    def c_add_tag_synonym(self, tag_id, value):
        return self.add_tag(tag_id, value)


class TagerTaggingResultDbu():
    def get_by_id(self, imp_catalog_page_id):
        log.info('Search tagging result by id %r', imp_catalog_page_id)
        return db.session.query(
            TagerTaggingResult.id,
            TagerTaggingResult.imp_catalog_page_id,
            TagerTaggingResult.name,
            TagerTaggingResult.orginal_title,
            TagerTaggingResult.brand,
        ).filter(
            and_(
                TagerTaggingResult.imp_catalog_page_id == imp_catalog_page_id,
                TagerTaggingResult.active.is_(True)
            )
        ).one_or_none()

    def get_by_name(self, name):
        return db.session.query(
            TagerTaggingResult.id,
            TagerTaggingResult.imp_catalog_page_id,
            TagerTaggingResult.name,
            TagerTaggingResult.orginal_title,
            TagerTaggingResult.brand,
        ).filter(
            and_(
                TagerTaggingResult.name == name,
                TagerTaggingResult.active.is_(True)
            )
        ).all()

    def is_exists(self, imp_catalog_page_id):
        return self.get_by_id(imp_catalog_page_id)

    def add_tagging_result(self, dct_tagging_result):
        tagging_result = self.is_exists(dct_tagging_result.get('imp_catalog_page_id'))
        log.info('Taging result %r', tagging_result)
        if not tagging_result:
            t = TagerTaggingResult(**dct_tagging_result)
            db.session.add(t)
            tagging_result = t
        else:
            log.info('Change tagging_result IcpID: {} old: {} -> new: {}'.format(
                tagging_result.imp_catalog_page_id,
                tagging_result.name,
                dct_tagging_result.get('title')
                )
            )
            t = TagerTaggingResult.query.filter(
                TagerTaggingResult.id == tagging_result.id
            ).first()

            t.name = dct_tagging_result.get('name')
            t.orginal_title = dct_tagging_result.get('orginal_title')
            t.brand = dct_tagging_result.get('brand')
            t.last_update_date = datetime.datetime.now()
            t.last_update_by = 1

        db.session.flush()
        return tagging_result.id

    @commit_after_execution
    def c_add_tagginig_result(self, dct_tagging_result):
        return self.add_tagging_result(dct_tagging_result)

    def get_list_results_by_string(self, tag):
        ilike_tag = '%{}%'.format(tag)
        return db.session.query(
            TagerTaggingResult.imp_catalog_page_id,
            TagerTaggingResult.orginal_title.label('title')
        ).filter(
            func.lower(TagerTaggingResult.orginal_title).ilike(ilike_tag)
        ).all()

    @commit_after_execution
    def update_results_tags(self, tag):
        ilike_tag = '%{}%'.format(tag)
        updated_rows = (
            db.session.query(TagerTaggingResult)
            .filter(TagerTaggingResult.name.ilike(ilike_tag))
            .update({TagerTaggingResult.name: func.replace(TagerTaggingResult.name, tag, '')},
                    synchronize_session=False)
            )
        log.info("Updated {} rows".format(updated_rows))

    def search_brand_in_title(self, imp_catalog_page_id, title):
        query = """
with params as (
    select
        :title as title
)
,selected as (
        select
            tbs.value,
            row_number() over(partition by tbs.tager_brand_id order by char_length(tbs.value) DESC) pos
        from params p
        join tager_brand_synonym tbs on tbs.active  is true and position(tbs.value in p.title) > 0
)
select s.value from selected s where pos = 1 order by char_length(s.value) desc
"""
        return db.session.execute(query, {'title': title}).fetchall()

    def search_category_in_title(self, imp_catalog_page_id, title):
        query = """
with params as (
select
    :title as title
)
,selected as (
    select
        tcs.value,
        row_number() over(partition by tcs.tager_category_id order by char_length(tcs.value) DESC) pos
    from params p
    join tager_category_synonym tcs on position(tcs.value in p.title) > 0 and tcs.active is true
)
select value from selected where pos = 1 order by char_length(value) desc
"""
        return db.session.execute(query, {'title': title}).fetchall()

    def search_color_in_title(self, imp_catalog_page_id, title):
        query = """
with params as (
select
    :title as title
)
,selected as (
    select
        tcs.value,
        row_number() over(partition by tcs.tager_color_id order by char_length(tcs.value) DESC) pos
    from params p
    join tager_color_synonym tcs on position(tcs.value in p.title) > 0 and tcs.active is true
)
select value from selected where pos = 1 order by char_length(value) desc
"""
        return db.session.execute(query, {'title': title}).fetchall()

    def search_tag_in_title(self, imp_catalog_page_id, title):
        query = """
with params as (
select
    :title as title
)
,selected as (
    select
        tts.value,
        row_number() over(partition by tts.tager_tag_id order by char_length(tts.value) DESC) pos
    from params p
    join tager_tag_synonym tts on position(tts.value in p.title) > 0 and tts.active is true
)
select value from selected where pos = 1 order by char_length(value) desc
"""
        return db.session.execute(query, {'title': title}).fetchall()

    def search_size_in_title(self, imp_catalog_page_id, title):
        query = """
with params as (
select
    :title as title
)
,selected as (
    select
        ts.name,
        row_number() over(partition by ts.id order by char_length(ts.name) DESC) pos
    from params p
    join tager_size ts on position(ts.name in p.title) > 0 and ts.active is true
)
select name from selected where pos = 1 order by char_length(name) desc
"""
        return db.session.execute(query, {'title': title}).fetchall()

    def get_definition_result(self, imp_catalog_page_id=None):
        result = db.session.query(
            TagerTaggingResult.id,
            TagerTaggingResult.imp_catalog_page_id,
            TagerTaggingResult.name,
            TagerTaggingResult.orginal_title,
            TagerTaggingResult.brand,
            TagerCategoryAssignment.category,
            TagerCategoryAssignment.rate
        ).join(
            TagerCategoryAssignment,
            TagerCategoryAssignment.imp_catalog_page_id == TagerTaggingResult.imp_catalog_page_id
        )
        if imp_catalog_page_id:
            result = result.filter(
                TagerTaggingResult.imp_catalog_page_id == imp_catalog_page_id
            )
        return result.all()


class TagerSizeDbu():
    def _get_all(self):
        return db.session.query(
            TagerSize.id,
            TagerSize.name,
            TagerSize.meaning,
            TagerSize.active,
            TagerSize.deleted
        )

    def get_all(self):
        return self._get_all().filter(
            and_(
                TagerSize.active.is_(True),
                TagerSize.deleted.isnot(True)
            )
        ).all()

    def get_by_id(self, size_id: int):
        return self._get_all().filter(
            and_(
                TagerSize.id == size_id,
                TagerSize.active.is_(True),
                TagerSize.deleted.isnot(True)
            )
        ).first()

    def get_by_name(self, name: str):
        return self._get_all().filter(
            and_(
                TagerSize.name == name,
                TagerSize.active.is_(True),
                TagerSize.deleted.isnot(True)
            )
        ).first()

    def get_by_meaning(self, meaning: str):
        return self._get_all().filter(
            and_(
                TagerSize.name == meaning,
                TagerSize.active.is_(True),
                TagerSize.deleted.isnot(True)
            )
        ).all()

    def is_exists(self, name: str) -> bool:
        size = self.get_by_name(name)
        if size:
            return size
        return None

    def add(self, name, meaning):
        result = self.is_exists(name)
        if not result:
            pd = TagerSize(name, meaning)
            db.session.add(pd)
            db.session.flush()
            result = pd
        else:
            pd = TagerSize.query.filter(
                and_(
                    TagerSize.name == name,
                    TagerSize.meaning == meaning
                )
            ).first()
            pd.name = name
            pd.meaning = meaning
            pd.last_update_by = datetime.datetime.now()
            pd.last_update_by = 1
            db.session.flush()
            result = pd
        return result

    @commit_after_execution
    def c_add(self, name, meaning):
        return self.add(name, meaning)
