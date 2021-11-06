# from celery import Celery

import time
# import redis
from price.modules.imp_price.services import Services as PpServices 
from price.modules.price.services import Services as PriceServices
from price.modules.price.tags_product import TagsProduct
from price.utils.dict_utils import sa_obj_to_dict 
from price import celery_app

import logging
log = logging.getLogger(__name__)

"""
def connect():
    return redis.Redis(host="192.168.254.201", port=6379, db=10)
"""

@celery_app.task
def product_page_parase(result):
    pps = PpServices()
    pps.process_product_pages(result)

@celery_app.task
def download_catalog(entry_point_id):
    s = PriceServices()
    s.run_entry_points(entry_point_id)
    

@celery_app.task
def c_tags_product(ofert_id=None, shop_id=None, entry_point_id=None, date_scan=None): 
    ps = PriceServices()
    for lp, ofert in ps.get_ofert_for_tags(ofert_id=None, shop_id=None, entry_point_id=None, scan_date=None):
        if lp % 1000 == 0:
            log.info('Order ofert no: {}'.format(lp))
        tag_paraser.delay(sa_obj_to_dict(ofert))
    log.info('Order {} pferts'.format(lp))


@celery_app.task
def tag_paraser(d_ofert):
    tp = TagsProduct()
    tp.tag_parser(None, d_ofert)


# @celery_app.task
# def proces_not_parased_page(self):
#     ps = PpServices() 
#     ps.process_new_product_pages()
