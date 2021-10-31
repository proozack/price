import contextlib
import functools

from price import db

import logging
log = logging.getLogger(__name__)


def rollback():
    db.session.rollback()


def commit():
    db.session.commit()


@contextlib.contextmanager
def commit_section():
    try:
        yield None
        commit()

    except:  # noqa: E722
        rollback()
        raise


def commit_after_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with commit_section():
            return func(*args, **kwargs)

    return wrapper
