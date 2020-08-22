from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, types, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import Text
import collections

from app import db
from datetime import datetime


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


class MyMixin():
    __abstract__ = True
    __mapper_args__= {'always_refresh': True}
    
    id =  Column(Integer, primary_key=True)
    creation_date = Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = 'PK record')
    created_by = Column(Integer, nullable=False, comment = 'Who created record')
    last_update_date = Column(db.DateTime, nullable=True, comment = 'Timestamp last update record')
    update_last_by = Column(Integer, nullable=True, comment='Who last update record')
    active = Column(Boolean, nullable=False, default=True, comment = 'Is record is active')
    deleted = Column(Boolean, nullable=False, default=False, comment = 'Is record is deleted')
    # parmas = Column(JSONEncodedDict, default=[], nullable=True, comment='Additional space for data storage for the record')  #aktualnie nie mam postgresa który by to suportował


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
            for field in self.__dir__() if field[0:1] != '_' and not isinstance(getattr(self, field), collections.Callable) and field not in wrong_list
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
    __mapper_args__= {'always_refresh': True}

    arch_id =  Column(Integer, primary_key=True)

    def __init__(self):
        pass
