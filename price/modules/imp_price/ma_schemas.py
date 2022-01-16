from marshmallow import Schema, fields
from price.utils.marshmallow_tools import opt_str, req_int

import logging
log = logging.getLogger(__name__)


ImpCatalogPageStatusSchema = Schema.from_dict(
    {
        "imp_catalog_page_id": fields.Int(),
        "status_type": fields.Str(), 
    }
)
