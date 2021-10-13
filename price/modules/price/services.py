from app import db
import requests
from .db_utils import EntryPointsDbUtils
# from app.utils.local_type import Ofert
from app.utils.validator import is_web_page
from app.utils.download_utils import standard_request
from app.modules.ims.enrich_images import EnrichImages
from app.modules.price.models import Ofert
from app.modules.price.parser.visit import Visit
from app.modules.price.parser.page import Page
from app.modules.price.parser.gallery import GaleryParser
from app.modules.price.match_product import MatchProduct
from app.modules.price.tags_product import TagsProduct
from app.modules.price.normalize_product import NormalizeProduct
from app.modules.price.product_support import ProductSupport 
from app.modules.price.db_utils import KeyWordLinkDbUtils, TagWordLinkDbUtils, BrandDbUtils, CategorySynonymDbUtils, CategoryDbUtils
from app.modules.price.db_utils import CategoryDbUtils, ProductDbUtils

import logging
log = logging.getLogger(__name__)


class Services():
    def __init__(self):
        pass

    def run_entry_points(self, enty_point_id=None):
        ep = EntryPointsDbUtils()
        list_all_enty_points = ep.get_list_all_entry_points(enty_point_id)
        for id_point, url, category_id in list_all_enty_points:
            try:
                list_oferts = self.visit_sites(url)
                self.save_oferts(list_oferts, id_point)
            except:
                list_oferts = []
                log.warn('Can\'t parse entry point {} [{}]'.format(id_point, url), exc_info=True)
        self.enrich_images()

    def visit_sites(self, url: str) -> list:
        result_list = []
        while url:
            p = self.visit_site(url)
            result_list = list(set(result_list + p.entity))
            result_list = list(set(result_list + p.entity))
            self.last_url = url
            url = None if self.last_url == p.next_page else p.next_page
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
        log.info('Try save %r objects', len(objects))
        db.session.bulk_save_objects(objects)
        db.session.commit()
        log.info('Saved %r objects', len(objects))

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

    def get_list_category(self):
        cdbu = CategoryDbUtils()        
        result = cdbu.get_all_category()
        for item in result:
            log.info('%r', item)

    def parase_ofert(self, ofert_id=None, shop_id=None):
        ps = ProductSupport() 
        mp = MatchProduct()
        np = NormalizeProduct()
        for tp_ofert in ps.parase_all_ofert(ofert_id, shop_id):
            tp_ofert = mp.parse_offert(tp_ofert)
            tp_ofert = np.parse_offert(tp_ofert)
            tp_ofert = ps.save_product(tp_ofert)

    def tags_ofert(self, ofert_id=None, shop_id=None, entry_point_id=None):
        ps = ProductSupport()
        tp = TagsProduct()
        for lp, ofert in enumerate(ps.parase_all_ofert(ofert_id, shop_id, entry_point_id)):
            if lp % 1000 == 0:
                log.info('Parse: \t\t\t %r oferts', lp)
            tp.tag_parser(ofert)

    def add_synonym_to_category(self, category_id, word):
        """
        kwdu = KeyWordLinkDbUtils()
        id = kwdu.add_word_to_category(int(category_id), word.lower().strip())
        """
        csdbu = CategorySynonymDbUtils()
        id = csdbu.c_add_new_synonym(category_id, word.lower().strip())
        log.info('Add word\'s link under id {}'.format(id) )

    def add_tag_to_list(self, name, product_id):
        twldu = TagWordLinkDbUtils()
        id = twldu.add_tag(name.lower().strip(), int(product_id))
        log.info('Add tag\'s link under id {}'.format(id) )
    
    def add_loose_tag(self, name):
        twldu = TagWordLinkDbUtils()
        id = twldu.add_loose_tag(name.lower().strip())
        log.info('Add tag under id {}'.format(id) )

    def add_brand(self, brand_name, logo=None):
        bdu = BrandDbUtils()
        id = bdu.add_brand(brand_name.lower().strip(), logo)
        log.info('Add brand under id {}'.format(id) )

    def send_notification(self):
        ct = CategoryDbUtils()
        pd = ProductDbUtils()
        message = []
        category_list = ct.get_all_category()
        for category in category_list:
            list_id_products = [
                i[0]
                for i in pd.get_product_for_catgeory_view(category[0])
            ]
            message.append('{} -> {}'.format(category[1], len(list_id_products)))
        result = '\n'.join(message)
        print(result)

        data = {'message': result}
        r = requests.post('http://192.168.254.200:5000/send', data=data)
