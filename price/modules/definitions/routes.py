from price.extension import api
from price.modules.definitions.endpoints import (
    DefinitionsTest,
    DefinitionsMenu,
    DefinitionMetaCategory,
    DefinitionMetaCategoryAlt,
)

api.add_resource(DefinitionsTest, '/definitions_test')
api.add_resource(DefinitionsMenu, '/menu')
api.add_resource(DefinitionMetaCategory, '/definitions_meta_category/<string:name>')
api.add_resource(DefinitionMetaCategoryAlt, '/definitions_meta_category/<int:meta_category_id>')
