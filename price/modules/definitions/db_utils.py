import datetime
from price import db
from sqlalchemy import and_
from price.utils.db_transaction import commit_after_execution


from price.modules.definitions.models import (
    DefTypeCategory,
    DefGroupCategory,
    DefMetaCategory,
    DefBrand,
)

import logging
log = logging.getLogger(__name__)


class DefTypeCategoryDbu():
    def _get_all(self):
        return db.session.query(
            DefTypeCategory.id,
            DefTypeCategory.name
        ).filter(
            DefTypeCategory.active.is_(True)
        )

    def get_all(self):
        return self._get_all().all()

    def get_by_id(self, id):
        return self._get_all().filter(
            DefTypeCategory.id == id
        ).one_or_none()

    def get_by_name(self, name):
        return self._get_all().filter(
            DefTypeCategory.name == name
        ).all()

    def is_exists(self, name):
        return self.get_by_name(name)

    def add(self, name, active=True, deleted=False):
        dtc = self.is_exists(name)
        if not dtc:
            dtc = DefTypeCategory(name)
            db.session.add(dtc)
            db.session.flush()
        else:
            dtc = DefTypeCategory.query.filter(
                DefTypeCategory.id == dtc.id
            )
            dtc.name = name
            dtc.active = active
            dtc.deleted = deleted
            dtc.last_update_date = datetime.datetime.now()
            dtc.last_update_by = 1
            db.session.flush()
        return dtc

    @commit_after_execution
    def c_add(self, name, active=True, deleted=False):
        return self.add(name, active, deleted)


class DefGroupCategoryDbu():
    def _get_all(self):
        return db.session.query(
            DefGroupCategory.id,
            DefGroupCategory.def_type_category_id,
            DefGroupCategory.name,
            DefGroupCategory.logo,
            DefGroupCategory.description,
            DefGroupCategory.slug
        ).filter(
            DefGroupCategory.active.is_(True)
        )

    def get_by_id(self, id):
        return self._get_all().filter(
            DefGroupCategory.id == id
        ).one_or_none()

    def get_by_name(self, name):
        return self._get_all().filter(
            DefGroupCategory.name == name
        ).all()

    def get_by_def_def_type_category_id(self, def_type_category_id):
        return self._get_all().filter(
            DefGroupCategory.def_type_category_id == def_type_category_id
        ).all()

    def is_exists(self, def_type_category_id, name):
        return db.session.query(
            DefGroupCategory.id
        ).filter(
            and_(
                DefGroupCategory.def_type_category_id == def_type_category_id,
                DefGroupCategory.name == name,
                DefGroupCategory.active.is_(True)
            )
        ).one_or_none()

    def add(self, def_type_category_id, name, logo=None, description=None, slug=None, active=True, deleted=False):
        dgc = self.is_exists(def_type_category_id, name)
        if not dgc:
            dgc = DefGroupCategory(def_type_category_id, name, logo, description, slug)
            db.session.add(dgc)
            db.session.flush()
        else:
            dgc = DefGroupCategory.query.filter(
                and_(
                    DefGroupCategory.def_type_category_id == def_type_category_id,
                    DefGroupCategory.name == name,
                    DefGroupCategory.active.is_(True)
                )
            )
            dgc.name = name
            dgc.logo = logo
            dgc.description = description
            dgc.slug = slug
            dgc.active = active
            dgc.deleted = deleted
            dgc.last_update_by = 1
            dgc.last_update_date = datetime.datetime.now()
            db.session.flush()
        return dgc

    @commit_after_execution
    def c_add(self, def_type_category_id, name, logo=None, description=None, slug=None, active=True, deleted=False):
        return self.add(def_type_category_id, name, logo, description, slug, active, deleted)


class DefMetaCategoryDbu():
    def _get_all(self):
        return db.session.query(
            DefMetaCategory.id,
            DefMetaCategory.def_group_category_id,
            DefMetaCategory.name,
            DefMetaCategory.logo,
            DefMetaCategory.description,
            DefMetaCategory.slug
        ).filter(
            DefMetaCategory.active.is_(True)
        )

    def get_by_id(self, id):
        return self._get_all().filter(
            DefMetaCategory.id == id
        ).one_or_none()

    def get_by_name(self, name):
        return self._get_all().filter(
            DefMetaCategory.name == name
        ).one_or_none()

    def get_by_def_group_category_id(self, def_group_category_id):
        return self._get_all().filter(
            DefMetaCategory.def_group_category_id == def_group_category_id
        ).all()

    def is_exists(self, def_group_category_id, name):
        return db.session.query(
            DefMetaCategory.id
        ).filter(
            and_(
                DefMetaCategory.def_group_category_id == def_group_category_id,
                DefMetaCategory.name == name,
                DefMetaCategory.active.is_(True)
            )
        ).one_or_none()

    def add(self, def_group_category_id, name, logo=None, description=None, slug=None, active=True, deleted=False):
        dgc = self.is_exists(def_group_category_id, name)
        if not dgc:
            dgc = DefMetaCategory(def_group_category_id, name, logo, description, slug)
            db.session.add(dgc)
            db.session.flush()
        else:
            dgc = DefMetaCategory.query.filter(
                and_(
                    DefMetaCategory.def_group_category_id == def_group_category_id,
                    DefMetaCategory.name == name,
                    DefMetaCategory.active.is_(True)
                )
            )
            dgc.name = name
            dgc.logo = logo
            dgc.description = description
            dgc.slug = slug
            dgc.active = active
            dgc.deleted = deleted
            dgc.last_update_by = 1
            dgc.last_update_date = datetime.datetime.now()
            db.session.flush()
        return dgc

    @commit_after_execution
    def c_add(self, def_group_category_id, name, logo=None, description=None, slug=None, active=True, deleted=False):
        return self.add(def_group_category_id, name, logo, description, slug, active, deleted)

    def get_menu(self):
        return db.session.query(
            DefMetaCategory.id.label('meta_category_id'),
            DefMetaCategory.def_group_category_id,
            DefMetaCategory.name.label('meta_category_name'),
            DefGroupCategory.def_type_category_id,
            DefGroupCategory.name.label('group_category_name'),
            DefTypeCategory.id.label('type_category_id'),
            DefTypeCategory.name.label('type_category_name')
        ).join(
            DefGroupCategory,
            and_(
                DefMetaCategory.def_group_category_id == DefGroupCategory.id,
                DefGroupCategory.active.is_(True)
            )
        ).join(
            DefTypeCategory,
            and_(
                DefTypeCategory.id == DefGroupCategory.def_type_category_id,
                DefTypeCategory.active.is_(True)
            )
        ).filter(
            DefMetaCategory.active.is_(True)
        ).order_by(
            DefTypeCategory.name,
            DefGroupCategory.name,
            DefMetaCategory.name
        ).all()


class DefBrandDbu():
    def _get_all(self):
        return db.session.query(
            DefBrand.id,
            DefBrand.name,
            DefBrand.logo,
            DefBrand.slogan,
            DefBrand.description,
            DefBrand.brands_url
        ).filter(
            DefBrand.active.is_(True)
        )

    def get_by_id(self, id):
        return self._get_all().filter(
            DefBrand.id == id
        ).one_or_none()

    def get_by_name(self, name):
        return self._get_all().filter(
            DefBrand.name == name
        ).all()

    def is_exists(self, name):
        return db.session.query(
            DefBrand.id
        ).filter(
            and_(
                DefBrand.name == name,
                DefBrand.active.is_(True)
            )
        ).one_or_none()

    def add(self, name, logo=None, slogan=None, description=None, brands_url=None, active=True, deleted=False):
        dgc = self.is_exists(name)
        if not dgc:
            dgc = DefBrand(name, slogan, logo, description, brands_url)
            db.session.add(dgc)
            db.session.flush()
        else:
            dgc = DefBrand.query.filter(
                and_(
                    DefBrand.name == name,
                    DefBrand.active.is_(True)
                )
            )
            dgc.name = name
            dgc.slogan = slogan
            dgc.logo = logo
            dgc.description = description
            dgc.brands_url = brands_url
            dgc.active = active
            dgc.deleted = deleted
            dgc.last_update_by = 1
            dgc.last_update_date = datetime.datetime.now()
            db.session.flush()
        return dgc

    @commit_after_execution
    def c_add(self, name, slogan=None, logo=None, description=None, brands_url=None, active=True, deleted=False):
        return self.add(name, slogan, logo, description, brands_url, active, deleted)
