from app.utils.local_type import Ofert, TempProduct
from app.utils.string_utils import StringUtils
from app.modules.price.db_utils import TagProductDbUtils, TagOfertDbUtils, TagDbUtils, BrandDbUtils, CategoryDbUtils
from app.modules.price.tools import BrandTools, CategorySynonymTools

import logging
log = logging.getLogger(__name__)

skip_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~']



class TagsProduct():
    def __init__(self):
        self.pt = BrandTools()
        self.bdbu = BrandDbUtils()
    
    def tag_parser(self, ofert: Ofert):
        su = StringUtils()
        tp = TempProduct(**self.sa_obj_to_dict(ofert))

        tp = self.manage_category(tp)
        tp = self.manage_manufacturer(tp)        

        if tp.title:
            tags_list = [
                tag
                # for tag in tp.title.split(' ') if tag not in skip_characters and tag != ''
                for tag in su.multisplit_string(tp.title, lower=True) if tag not in skip_characters and tag != ''
            ]
            # log.info('TP: %r -> %r\t%r', tp.id,  tp.url, tags_list)
            if hasattr(tp, 'brand_id') and hasattr(tp, 'category_id'):
                self.save_tags_list(tags_list, tp.id, tp.brand_id, tp.category_id)

    def save_tags_list(self, tags_list, ofert_id, brand_id, category_id):
        tags_string = ';'.join(tags_list)
        tpdbu = TagProductDbUtils()
        todbu = TagOfertDbUtils()
        tdu = TagDbUtils()

        tags_list_tuple = tdu.get_bulk_tags(tags_string)
        list_new_tags = [
            tags[1]
            for tags in tags_list_tuple if tags[0] is None
        ]
        # log.info('lIST new tags %r for %r', tags_list_tuple, tags_string)

        tdu.c_bulk_save_tag(list_new_tags)
        
        tags_list = [
            tag[1]
            for tag in tags_list_tuple if tag[2] is None
        ]

        log.info('Lisat tagów po której będzie wyszukiwany produkt %r', tags_list)

        result = tpdbu.get_product_by_tags_list(tags_list, category_id, brand_id)
        # result = tpdbu.get_product_by_tags_list(tags_string, category_id, brand_id)
        log.info('Wynik wyszukiwania %r', result)
        if isinstance(result, list):
            # log.info('Dupa')
            if len(result) > 0:
                product_id = result[0]
                product_id = product_id[0]
            else: 
               product_id = None
        else:
            product_id = result

        if product_id:
            # log.info('Products found list %r', product_id)
            todbu.c_save_ofert_to_product(ofert_id, product_id)
        else:
            todbu.c_register_product_by_tags(tags_list, ofert_id, brand_id, category_id)

    def manage_manufacturer(self, tp):
        title_manufacturer = self.pt.search_brand(tp.title)
        page_manufacturer = None

        if tp.manufacturer:
            title = self.pt.remove_brand_from_title(tp.title, tp.manufacturer)
            if tp.title != title[0]:
                log.info('Remove manufacturer (form page) from title %r -> %r', tp.title, title[0])
                tp.title = title[0]


            # dodać logowanie jeśli nie znajdzie producenta na liście producentów (lub opisać żeby automatycznie dodało)
            brand_id = self.bdbu.get_brand_id_by_name(tp.manufacturer.lower())
            if not brand_id:
                brand_id = self.bdbu.new_brand(tp.manufacturer.lower())
            page_manufacturer = (brand_id, tp.manufacturer)
            log.info('Manufacturer found on page %r', page_manufacturer)

        # trzeba obsłużuć przypadek gdy nazwa jednego producenta = nazwie produktu innego producenta
        if title_manufacturer:
            log.info('Manufacturer found in title: %r', title_manufacturer)
            title = self.pt.remove_brand_from_title(tp.title, title_manufacturer)
            if tp.title != title[0]:
                log.info('Remove manufacturer (form title) from title %r -> %r', tp.title, title[0])
                tp.title = title[0]

        if page_manufacturer:
            tp.add_field('brand_id', page_manufacturer[0])
            log.info('I use manufacturer from page %r', tp.manufacturer)
        elif title_manufacturer:
            tp.add_field('brand_id', title_manufacturer[0])
            tp.manufacturer = title_manufacturer[1]
            log.info('I use manufacturer from title %r', title_manufacturer)
        else:
            log.warning('No found manufacturer, I skipping offert id: %r ', tp.id)
            return tp

        if tp.title != title[0]:
            # log.info('Remove brnad %r from title %r -> %r', manufacturer, tp.title, title[0])
            tp.title = title[0]
        return tp

    # def find_brand_by_tags(self, tgs_list):


    def manage_category(self, tp):
        cst = CategorySynonymTools()
        cdbu = CategoryDbUtils()
        synonym = cst.search_catgeory_name(tp.title)
        log.info('Znaleziony synonim %r', synonym)
        if synonym:
            title = cst.remove_category_from_title(tp.title, synonym[1])
            if tp.title != title:
                log.info('Synonym change from  %r to %r', tp.title, title[0])
                tp.title = title[0]
                tp.category_id = synonym[0]
                tp.category_name = cdbu.get_category_name_by_id(synonym[0])
        return tp

    def sa_obj_to_dict(self, sa_object):
        result = {}
        for field in sa_object._fields:
            result[field] = getattr(sa_object, field, None)
        return result
