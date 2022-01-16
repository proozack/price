#!/usr/bin/env python3
import logging
# from price import create_app
from app import application
from price import db
from flask_script import Manager
from price.utils.rest_util import get
from price.modules.ims.enrich_images import EnrichImages
from price.modules.price.services import Services as PriceServices
from price.modules.imp_price.services import Services as ImpPriceServices
from price.modules.product.services import Services as ProductPriceServices

# app = create_app()

log = logging.getLogger(__name__)

manager = Manager(application)


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
def tags_ofert(ofert_id=None, shop_id=None, entry_point_id=None, date_scan=None):
    scan_date = date_scan
    """
    Run tags ofert
    """
    if ofert_id:
        log.info('Run parasing ofert: Ofert_id:{}'.format(ofert_id))
    elif shop_id:
        log.info('Run parasing ofert: Shop_id:{}'.format(shop_id))
    elif entry_point_id:
        log.info('Run parasing ofert: Entry_Point_id:{}'.format(entry_point_id))
    elif scan_date:
        log.info('Run parasing ofert: Scan Date: :{}'.format(scan_date))
    else:
        log.info('Run parasing all oferts')
    s = PriceServices()
    s.tags_ofert(ofert_id, shop_id, entry_point_id, scan_date)


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
    # with app.app_context():
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
    Run parasing product page for shop_id, synchronous commissioning
    """
    s = ImpPriceServices()
    s.parase_product_pages(shop_id)


@manager.command
def run_parasing_pages(shop_id=None, url_str=None, entry_point_id=None, limit=None, interval=None):
    """
    Run parasing product page for shop_id, Run as task celery
    """
    import time
    from price.tasks import product_page_parase
    ipp = ImpPriceServices()
    if limit is not None:
        limit = int(limit) - 1
    oi = 0
    for oi, result in enumerate(ipp.get_pages(shop_id, url_str, entry_point_id)):
        if limit is not None and oi > limit:
            log.info('I stop working because a limit has been set: {}'.format(limit + 1))
            break
        log.info('I order url processing: {}'.format(result.url))
        product_page_parase.delay(result)
        if interval:
            log.info('Wait ... {} s.'.format(interval))
            time.sleep(int(interval))
    log.info('I oreder {} tasks'.format(oi))


@manager.command
def run_downloading_ep(entry_point_id):
    """
    Run downloading page for entry_point_id, run as celery task
    """
    from price.tasks import download_catalog
    ipp = ImpPriceServices() # noqa F841
    download_catalog.delay(entry_point_id)


@manager.command
def c_tags_product(ofert_id=None, shop_id=None, entry_point_id=None, date_scan=None):
    from price.tasks import c_tags_product
    c_tags_product.delay(ofert_id, shop_id, entry_point_id, date_scan)


@manager.command
def proces_not_parased_page(entry_point_id=None):
    ipp = ImpPriceServices()
    if entry_point_id:
        log.info('Processing entry point ID: %r', entry_point_id)
        run_parasing_pages(None, None, entry_point_id)
    else:
        for entry_point_id in ipp.get_processed_entry_points():
            log.info('Processing entry point ID: %r', entry_point_id)
            run_parasing_pages(None, None, entry_point_id)


@manager.command
def tag_brand(imp_catalog_page_id=None, creation_date=None):
    from price.modules.imp_price.services import Services
    from price.tasks import add_brand_assignment
    s = Services()
    for imp_catalog_page_id in s.get_list_pages(imp_catalog_page_id, creation_date):
        log.info('Order tag brand {}'.format(imp_catalog_page_id))
        tp = s.get_tagging_product(imp_catalog_page_id)
        add_brand_assignment.delay(tp)


@manager.command
def tag_unprocessed(scan_date=None):
    from price.modules.imp_price.services import Services
    from price.tasks import add_brand_assignment, add_category_assignment
    s = Services()
    for imp_catalog_page_id in s.get_unprocessed_pages(scan_date):
        log.info('Order Imp_catalog_page: {}'.format(imp_catalog_page_id))
        tp = s.get_tagging_product(imp_catalog_page_id)
        add_brand_assignment.delay(tp)
        add_category_assignment.delay(tp)


@manager.command
def add_brnad_synonym(value):
    from price.modules.tager.services import Services
    s = Services()
    s.add_brnad_synonym(value)


@manager.command
def add_category_synonym(value):
    from price.modules.tager.services import Services
    from price.modules.imp_price.services import Services as ImpServices
    from price.tasks import add_category_assignment
    s = Services()
    imps = ImpServices()
    s.add_category_synonym(value)
    list_imp_catalog_page_id = get('http://127.0.0.1:7001/catalog_page_search/category/{}'.format(value))
    for imp_catalog_page_id in list_imp_catalog_page_id:
        tp = imps.get_tagging_product(imp_catalog_page_id)
        if tp:
            log.info('Order category_assignment ImpID: {} Title: {}'.format(
                imp_catalog_page_id,
                tp.get('catalog_title')
            ))
            add_category_assignment.delay(tp)
    for imp_catalog_page_id in list_imp_catalog_page_id:
        tp = imps.get_tagging_product(imp_catalog_page_id)
        if tp:
            log.info('Order tagging_product ImpID: {} Title: {}'.format(imp_catalog_page_id, tp.get('catalog_title')))
            tagging_product(imp_catalog_page_id, tp.get('catalog_title'))


@manager.command
def tag_category(imp_catalog_page_id=None, creation_date=None):
    from price.modules.imp_price.services import Services
    from price.tasks import add_category_assignment
    s = Services()
    for imp_catalog_page_id in s.get_list_pages(imp_catalog_page_id, creation_date):
        log.info('Order tag brand {}'.format(imp_catalog_page_id))
        tp = s.get_tagging_product(imp_catalog_page_id)
        add_category_assignment.delay(tp)


@manager.command
def add_color_synonym(value):
    from price.tasks import tagging_product
    from price.modules.tager.services import Services
    s = Services()
    tag = s.add_color_synonym(value)
    log.info('Tag %r', tag)
    for imp_catalog_page_id, title in s.get_list_results_by_string(tag):
        log.info('Order for tagging: {} ImpID: {}'.format(title, imp_catalog_page_id))
        tagging_product.delay(imp_catalog_page_id, title)


@manager.command
def add_tag_synonym(context, value):
    from price.tasks import tagging_product
    from price.modules.tager.services import Services
    s = Services()
    tag = s.add_tag_synonym(context, value)
    for imp_catalog_page_id, title in s.get_list_results_by_string(tag):
        log.info('Order for tagging: {} ImpID: {}'.format(title, imp_catalog_page_id))
        tagging_product.delay(imp_catalog_page_id, title)


@manager.command
def get_all_context():
    from price.modules.tager.services import Services
    s = Services()
    log.info('Liist context \n%r', s.get_all_context())


@manager.command
def add_tag_context(context):
    from price.modules.tager.services import Services
    s = Services()
    s.add_tag_context(context)


@manager.command
def tagging_product(imp_catalog_page_id=None, title=None):
    from price.tasks import tagging_product
    from price.modules.imp_price.services import Services
    s = Services()
    for imp_catalog_page_id, title in s.get_list_pages(imp_catalog_page_id):
        tagging_product.delay(imp_catalog_page_id, title)


@manager.command
def add_product_category(name, meta_category_id=None):
    from price.modules.product.services import Services
    s = Services()
    s.add_categroy(name, meta_category_id)


@manager.command
def copy_product():
    no = 0
    from price.tasks import copy_product
    ips = ImpPriceServices()
    for result in ips.get_all_price_for_catalog_page():
        # log.debug('Result %r', dir(result))
        copy_product.delay(result[0], result[1])
        if no % 1000 == 0:
            log.debug('Order {} task to copy product'.format(no))
        no = no+1


@manager.command
def add_product(imp_catalog_page_id, scan_date):
    ps = ProductPriceServices()
    ps.add_product(imp_catalog_page_id, scan_date)


@manager.command
def upadte_category():
    from price import db
    from price.modules.tager.models import TagerCategory
    from price.modules.product.db_utils import ProductCategoryDefDbu

    result = db.session.query(TagerCategory.name).filter(TagerCategory.active.is_(True)).all()
    pcd = ProductCategoryDefDbu()
    for cat in result:
        pcd.add_category(cat, 1)


if __name__ == "__main__":
    manager.run()
