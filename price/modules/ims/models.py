from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from price.utils.models import DbUtils
from datetime import datetime
import logging
log = logging.getLogger(__name__)


class UserBase(DbUtils):
    __abstract__ = True

    user_name = Column(String(50), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    user_type = Column(Integer, index=True, nullable=False, default=1)
    avatar = Column(String(200), nullable=True)
    passwd = Column(String(300), index=True, unique=False)
    pas_change_req = Column(Boolean, nullable=False, default=False)
    next_pas_change = Column(Date, nullable=True, default=datetime.now())
    is_authenticated = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    is_anonymous = Column(Boolean, nullable=False, default=False)


class User(UserBase):
    __tablename__ = 'ims_users'

    def __init__(self, name=None, email=None, passwd=None):
        self.user_name = name
        self.passwd = passwd
        self.email = email
        self.created_by = 1

    def __repr__(self):
        return '<User %r>' % (self.user_name)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id


class UserArch(UserBase):
    """Tabela archiwalna dla tabeli users"""
    __tablename__ = 'ims_users_arch'


class WorkerBase(DbUtils):
    __abstract__ = True
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdays = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    sex = Column(String(1), nullable=False, default='M')
    # user_id = Column(Integer, ForeignKey('ims_users.id'))

    @declared_attr
    def users_id(cls):
       return Column(ForeignKey('ims_users.id'))  # noqa E111

    @declared_attr
    def user(cls):
        return relationship("User")


class Worker (WorkerBase):
    __tablename__ = 'ims_workers'

    def __init__(self, first_name=None, last_name=None, sex=None):
        self.first_name = first_name
        self.last_name = last_name
        self.created_by = 1
        self.sex = sex

    def __repr__(self):
        return '<Worker %r %r>' % (self.first_name, self.last_name)


class ArchWorker(WorkerBase):
    """Tabela archiwalna dla tabeli users"""
    __tablename__ = 'ims_workers_arch'


class AuthLog(DbUtils):
    __tablename__ = 'ims_auth_log'

    login_used = Column(String(50), nullable=False)
    if_loged = Column(Boolean, nullable=False)
    message = Column(Text, nullable=True)

    def __init__(self, login_used=None, if_loged=False, message='authentication will not succeed'):
        self.login_used = login_used
        self.if_loged = if_loged
        self.created_by = 1
        self.message = message

    def __repr__(self):
        return '<Auth %r %r>' % (self.login_used, self.if_loged)
