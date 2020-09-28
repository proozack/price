#!/usr/bin/env python3
import logging
from flask_script import Manager
from app import create_app
from app import db
from app.modules.ims.enrich_images import EnrichImages
from app.modules.price.services import Services as PriceServices
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
def enrich_image():
    """
    Run enriching images process
    """
    log.info('Start enrich images ... ')
    with app.app_context():
        e = EnrichImages()
        e.parase_all_images()


@manager.command
def add_entry_point(url):
    """
    Add entry point to resources
    """
    print('Add entry point to resources {}'.format(url))


@manager.command
def parse_page(url):
    """
    Parse page without results save - using for testing parsing
    """
    log.info('Started parase page, url: %r', url)
    ps = PriceServices()
    p = ps.visit_site(url)
    for items in p.entity:
        log.info(items)


@manager.command
def run_downloading(enty_point_id=None):
    """
    Run parasing all entry point defined in price_enty_point
    """
    print('Run parasing all enty points')
    s = PriceServices()
    s.run_entry_points()


@manager.command
def enrich_images(enty_point_id=None):
    """
    Run enriching images
    """
    log.info('Run enriching images')
    s = PriceServices()
    s.enrich_images()


if __name__ == "__main__":
    manager.run()
