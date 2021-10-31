# -*- coding: utf8 -*-
import logging

import celery.signals
from celery import Task
from celery.exceptions import Retry
#from .extensions import db
from price import db

log = logging.getLogger(__name__)


def mk_base_task(app):
    class BaseTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            # from windar_api.db_util.feature_flags import get_all_flags_from_celery_task
            # fflags = get_all_flags_from_celery_task(self)
            rq = self.request
            with app.test_request_context():
                log.info('Start zadania %s (id: %s)', self.name, rq.id)
                log.debug('Parametry zadania %s\nargs: %r\nkwargs: %r', rq.id, args, kwargs)
                # if fflags:
                #     log.debug('Feature flags wymuszone przez headers: %r', fflags)
                try:
                    ret = Task.__call__(self, *args, **kwargs)
                    db.session.commit()
                    # db_kplus.session.commit()
                except Retry:
                    db.session.rollback()
                    # db_kplus.session.rollback()
                    raise
                except Exception:
                    db.session.rollback()
                    # db_kplus.session.rollback()
                    log.error('Blad w trakcie wykonywania zadania %s (id: %s)', self.name, rq.id, exc_info=True)
                    raise
                else:
                    log.info('Koniec zadania %s (id: %s)', self.name, rq.id)
                    return ret

    return BaseTask


@celery.signals.before_task_publish.connect
def before_task_publish(sender=None, body=None, headers=None, **kwargs):
    pass
    """
    if headers is not None:
        from windar_api.db_util.feature_flags import get_all_forced_flags
        forced = get_all_forced_flags()
        if forced:
            headers['forced_feature_flags'] = forced
    """
