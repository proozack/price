#!/usr/bin/env python3
import logging
from flask_script import Manager
from app import create_app
from app import db
from app.modules.ims.enrich_images import EnrichImages
from app.modules.price.services import Services as PriceServices
from app.modules.imp_price.services import Services as ImpPriceServices
# from app.modules.ims.models import Image

app = create_app()
log = logging.getLogger(__name__)

manager = Manager(app)


@manager.shell
def _shell_context():
    ret = dict(
       app=manager.app,
       db=db,
       # celery_app=celery_app,
    )
    """
    try:
        import exploration
        ret['exp'] = exploration
    except Exception:
        logging.getLogger().info('Blad import exploration', exc_info=True)
    """
    return ret


@manager.command
def try_parse_page(url):
    """
    Parse page without results save - using for testing parsing
    """
    log.info('Started parase page, url: %r', url)
    ps = PriceServices()
    p = ps.visit_site(url)
    for items in p.entity:
        log.info(items)


@manager.command
def try_get_next_page(url):
    """
    Parse page without results save - using for testing parsing
    """
    log.info('Started parase page, url: %r', url)
    ps = PriceServices()
    p = ps.test_next_page(url) # noqa F841


@manager.command
def add_entry_point(entry_point, category_id):
    """
    Add entry point do db
    """
    log.info('Try add entry point %r %r', entry_point, category_id)
    ps = PriceServices()
    p = ps.add_entry_point(entry_point, category_id) # noqa F841


@manager.command
def run_downloading(enty_point_id=None):
    """
    Run parasing all entry point defined in price_enty_point
    """
    print('Run parasing all enty points')
    s = PriceServices()
    s.run_entry_points(enty_point_id)


@manager.command
def parse_ofert(ofert_id=None, shop_id=None):
    """
    Run parasing all ofert storage in price_ofert
    """
    if ofert_id:
        log.info('Run parasing ofert: Ofert_id:{}'.format(ofert_id))
    elif shop_id:
        log.info('Run parasing ofert: Shop_id:{}'.format(shop_id))
    else:
        log.info('Run parasing all oferts')
    s = PriceServices()
    s.parase_ofert(ofert_id, shop_id)


@manager.command
def tags_ofert(ofert_id=None, shop_id=None, entry_point_id=None):
    """
    Run tags ofert
    """
    if ofert_id:
        log.info('Run parasing ofert: Ofert_id:{}'.format(ofert_id))
    elif shop_id:
        log.info('Run parasing ofert: Shop_id:{}'.format(shop_id))
    elif entry_point_id:
        log.info('Run parasing ofert: Entry_Point_id:{}'.format(entry_point_id))
    else:
        log.info('Run parasing all oferts')
    s = PriceServices()
    s.tags_ofert(ofert_id, shop_id, entry_point_id)


@manager.command
def list_entry_point():
    """
    Show all entry points
    """
    print('Run parasing all enty points')
    s = PriceServices()
    s.get_list_entry_point()


@manager.command
def list_category():
    """
    Show all category
    """
    log.info('All category:')
    s = PriceServices()
    s.get_list_category()

@manager.command
def enrich_image():
    """
    Run enriching images process
    """
    log.info('Start enrich images ... ')
    with app.app_context():
        e = EnrichImages()
        e.parase_all_images()


@manager.command
def add_synonym_to_cat(category_id, word):
    """
    Add synonym to category 
    """
    log.info('Try add  word %r to category %r', word, category_id)
    s = PriceServices()
    s.add_synonym_to_category(category_id, word)


@manager.command
def add_tag_to_list(name, product_id):
    """
    Add tag to product 
    """
    log.info('Try add tag %r to product %r', name, product_id)
    s = PriceServices()
    s.add_tag_to_list(name, product_id)


@manager.command
def add_loose_tag(name):
    """
    Add tag to list 
    """
    log.info('Try add tag %r', name)
    s = PriceServices()
    s.add_loose_tag(name)


@manager.command
def add_brand(brand_name, logo=None):
    """
    Add tag to list 
    """
    log.info('Try add new brand %r', brand_name)
    s = PriceServices()
    s.add_brand(brand_name, logo)


@manager.command
def enrich_images(enty_point_id=None):
    """
    Run enriching images
    """
    log.info('Run enriching images')
    s = PriceServices()
    s.enrich_images()


@manager.command
def send_notification():
    s = PriceServices()
    s.send_notification()


@manager.command
def run_processing():
    run_downloading()
    tags_ofert()
    send_notification()


@manager.command
def copy_product_to_imp(scan_date=None):
    """
    Copy product from price_ofert to imp_product
    """
    log.info('Run copy product from price_ofert to imp_price')
    s = ImpPriceServices()
    if scan_date:
        count = s.copy_product_to_imp(scan_date)
    else:
        count = s.copy_product_to_imp()
    log.info('Copy {} objects'.format(count))


@manager.command
def copy_all_product_to_imp():
    """
    Copy all product from price_ofert to imp_product
    """
    log.info('Run copy all product from price_ofert to imp_price')
    s = ImpPriceServices()
    s.copu_all_produc_to_imp()

@manager.command
def try_download_page(url, show_log=False):
    """
    Try download and parse product page
    """
    s = ImpPriceServices()
    if show_log:
        show_log = bool(show_log)
    s.try_download_page(url, show_log)

@manager.command
def parase_product_pages(shop_id):
    """
    Try download and parse product page
    """
    s = ImpPriceServices()
    s.parase_product_pages(shop_id)

@manager.command
def run_parasing_pages(shop_id):
    from tasks import product_page_parase
    ipp = ImpPriceServices()
    for result in ipp.get_pages(shop_id):
        product_page_parase.delay(result)

if __name__ == "__main__":
    manager.run()
