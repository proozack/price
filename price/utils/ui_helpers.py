# -*- coding: utf-8 -*-
from flask import request
from .utils.resource import PrivateResource

import logging
log = logging.getLogger(__name__)


class UiRouterNavigation(PrivateResource):

    def post(self):
        data = request.get_json()
        from_path = (data.get('from') or {}).get('path')
        to_path = (data.get('to') or {}).get('path')
        log.info(
            'Nowa nawigacja w gui; parametry=%r',
            data,
            extra={'from_path': from_path, 'to_path': to_path},
        )
