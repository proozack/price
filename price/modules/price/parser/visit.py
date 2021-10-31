from typing import Callable
from dataclasses import dataclass
import time

from price.utils.base_model import BaseModel

import logging
log = logging.getLogger(__name__)


@dataclass
class Visit(BaseModel):

    def __init__(self):
        self._response = None
        self._url = None
        self._classification = None

        self.time_measure = {
            'start_time': None,
            'end_time': None,
            'run_time': None
        }

        self.classification = NotImplemented

    def set_visit_url(self, url: str, validator: Callable) -> bool:
        self._url = validator(url)
        if self._url:
            return True
        return False

    def downloader(self, download_method: Callable) -> bool:
        self.time_measure['start_time'] = time.process_time()
        self._response = download_method(self._url)
        self.time_measure['end_time'] = time.process_time()
        self.time_measure['run_time'] = round(self.time_measure['end_time'] - self.time_measure['start_time'], 4)
        return self._response

    def get_response(self):
        return self._response

    def get_property_as_dict(self) -> dict:
        return {
            'url': self._url,
            'start_time': self.time_measure.get('start_time'),
            'end_time': self.time_measure.get('end_time'),
            'run_time': self.time_measure.get('run_time'),
            'status_code': self._response.get_status_code(),
            'classification': self.classification,
        }

    def __repr__(self):
        return '<Visit url: {} [{} s.]>'.format(self._url, self.time_measure['run_time'])
