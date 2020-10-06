from app import db
from .db_utils import EntryPointsDbUtils
# from app.utils.local_type import Ofert
from app.modules.price.models import Ofert
from app.modules.price.parser.visit import Visit
from app.modules.price.parser.page import Page
from app.utils.validator import is_web_page
from app.utils.download_utils import standard_request
from app.modules.price.parser.gallery import GaleryParser
from app.modules.ims.enrich_images import EnrichImages
from app.modules.price.match_product import MatchProduct

import logging
log = logging.getLogger(__name__)


class Services():
    def __init__(self):
        pass

    def run_entry_points(self, enty_point_id=None):
        ep = EntryPointsDbUtils()
        list_all_enty_points = ep.get_list_all_entry_points(enty_point_id)
        for id_point, url in list_all_enty_points:
            list_oferts = self.visit_sites(url)
            self.save_oferts(list_oferts, id_point)
        self.enrich_images()

    def visit_sites(self, url: str) -> list:
        result_list = []
        while url:
            p = self.visit_site(url)
            result_list = list(set(result_list + p.entity))
            result_list = list(set(result_list + p.entity))
            self.last_url = url
            url = None if self.last_url == p.next_page else p.next_page
            # url = None
        # log.info('Objects %r', result_list)
        return result_list

    def visit_site(self, url: str) -> object:
        log.info('Visit site: {}'.format(url))
        v = Visit()
        v.set_visit_url(url, is_web_page)
        response = v.downloader(standard_request)
        # log.info('Response %r', response)
        p = Page(GaleryParser(), response)
        return p

    def test_next_page(self, url: str) -> object:
        while url:
            log.info('Entry to page:\t\t%r', url)
            p = self.visit_site(url)
            self.last_url = url
            url = None if self.last_url == p.next_page else p.next_page
            log.info('Next adress page is:\t\t%r', url)

    def save_oferts(self, list_oferts: list, entry_point_id: int) -> None:
        objects = [
            Ofert(result, entry_point_id)
            for result in list_oferts if result is not None
        ]
        log.info('Try save %r objexts', len(objects))
        db.session.bulk_save_objects(objects)
        db.session.commit()
        log.info('Saved %r objexts', len(objects))

    def enrich_images(self):
        e = EnrichImages()
        e.parase_all_images()

    def add_entry_point(self, entry_point, category_id):
        epdbu = EntryPointsDbUtils()
        epdbu.add_entry_point_with_check_shop(entry_point, category_id)

    def get_list_entry_point(self):
        epdbu = EntryPointsDbUtils()
        list_ep = epdbu.get_list_all_entry_points()
        for item in list_ep:
            log.info('%r', item)

    def parase_ofert(self, ofert_id=None, shop_id=None):
        mp = MatchProduct()
        for ofert in mp.parase_all_ofert(ofert_id, shop_id):
            log.info('To jest ofert %r', ofert)
            mp.parse_offert(ofert)
