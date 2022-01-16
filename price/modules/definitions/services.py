from price.modules.definitions.db_utils import (
    DefTypeCategoryDbu,
    DefGroupCategoryDbu,
    DefMetaCategoryDbu,
    DefBrandDbu
)
import logging
log = logging.getLogger(__name__)


class Services():
    def __init__(self):
        pass

    def get_all_type_category(self):
        dtc = DefTypeCategoryDbu()
        return dtc.get_all()

    def add_type_category(self, name):
        dtc = DefTypeCategoryDbu()
        dtc.c_add(name)

    def add_group_category(self, def_type_category_id, name):
        dgc = DefGroupCategoryDbu()
        dgc.c_add(def_type_category_id, name)

    def add_meta_category(self, def_group_category_id,  name):
        dmc = DefMetaCategoryDbu()
        dmc.c_add(def_group_category_id, name)

    def add_brand(self, name):
        db = DefBrandDbu(name)
        db.c_add(name)

    def get_menu(self):
        dmc = DefMetaCategoryDbu()
        return dmc.get_menu()

    def get_meta_category_id_by_name(self, name):
        dmc = DefMetaCategoryDbu()
        return dmc.get_by_name(name)

    def get_meta_category_by_id(self, meta_category_id):
        dmc = DefMetaCategoryDbu()
        return dmc.get_by_id(meta_category_id)
