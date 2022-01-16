from flask_restful import Resource
from price.modules.definitions.services import Services

import logging
log = logging.getLogger(__name__)


class DefinitionsTest(Resource):
    def get(self):
        s = Services()
        result = s.get_all_type_category()
        log.debug('Result %r ', result)
        return {
            'answert': 'HelloWorld',
            'data': result
        }


class DefinitionsMenu(Resource):
    def get(self):
        s = Services()
        return s.get_menu()


class DefinitionMetaCategory(Resource):
    def get(self, name):
        s = Services()
        return s.get_meta_category_id_by_name(name)


class DefinitionMetaCategoryAlt(Resource):
    def get(self, meta_category_id):
        s = Services()
        return s.get_meta_category_by_id(meta_category_id)
