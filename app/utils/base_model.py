import inspect
from inspect import isfunction
from functools import partial
import collections

import types


import logging
log = logging.getLogger(__name__)


class BaseModel():

    def __init__(self):
        pass

    def get_attributes_list(self) -> list:
        return [
            field
            for field in self.__dir__() if field[0:1] != '_' and not isinstance(getattr(self, field), collections.Callable)
        ]

    def set_attr_from_dict(self, **kwargs) -> None:
        attr_list = self.get_attributes_list()
        for key, value in kwargs.items():
            if key in attr_list:
                setattr(self, key, value)

    def get_clear_dict(self) -> dict:
        return {
            field: ''
            for field in self.get_attributes_list()
        }
