from flask import g
from sqlalchemy import Column, Integer, Boolean
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
import collections

from price import db
import datetime
# from conf.localconfig import Config# noqa F402

import logging
log = logging.getLogger(__name__)


"""
class JSONEncodedDict(types.TypeDecorator):
    impl = JSONB(none_as_null=True)
    python_type = dict

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return recursive_default_handler(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return recursive_default_handler(value)

    def coerce_compared_value(self, op, value):
        return self.impl.coerce_compared_value(op, value)
"""


def id_auth_user():
    try:
        return g.auth_user.login
    except AttributeError:
        return 1 # Config.PRICE_USER_ID


class MyMixin():
    __abstract__ = True
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)

    @declared_attr
    def active(cls):
        return Column(
            Boolean,
            nullable=False,
            default=True,
            comment='Is record is active'
        )

    @declared_attr
    def deleted(cls):
        return Column(
            Boolean,
            nullable=False,
            default=False,
            comment='Is record is deleted'
        )

    @declared_attr
    def created_by(cls):
        return Column(
            Integer,
            nullable=False,
            default=id_auth_user,
            comment='Who created record'
        )

    @declared_attr
    def creation_date(cls):
        return Column(
            db.DateTime,
            nullable=False,
            default=datetime.datetime.now,
            comment='Timestamp created record'
        )

    @declared_attr
    def last_update_by(cls):
        return Column(
            Integer,
            nullable=True,
            default=id_auth_user,
            comment='Who last update record'
        )

    @declared_attr
    def last_update_date(cls):
        return Column(
            db.DateTime,
            nullable=True,
            default=datetime.datetime.now(),
            comment='Timestamp last update record'
        )

    # parmas = Column(JSONEncodedDict, default=[], nullable=True,
    # comment='Additional space for data storage for the record')  #aktualnie nie mam postgresa który by to suportował


class DbUtils(db.Model, MyMixin):
    __abstract__ = True

    def __init__(self):
        pass

    def get_attributes_list(self) -> list:
        wrong_list = [
            'query',
            'metadata',
        ]
        return [
            field
            for field in self.__dir__() if field[0:1] != '_' and not isinstance(getattr(self, field), collections.Callable) and field not in wrong_list # noqa E501
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

    def get_dict(self) -> dict:
        attr_list = self.get_attributes_list()
        return {
            key: getattr(self, key)
            for key in attr_list
        }


class ArchUtils():
    __abstract__ = True
    __mapper_args__ = {'always_refresh': True}

    arch_id = Column(Integer, primary_key=True)

    def __init__(self):
        pass
