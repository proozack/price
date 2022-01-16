from price.extension import api
from price.modules.tager.endpoints import (
    TagerTest,
    TagerResult
)

api.add_resource(TagerTest, '/tager_test')
api.add_resource(
    TagerResult,
    '/tager_result/<int:imp_catalog_page_id>'
)
