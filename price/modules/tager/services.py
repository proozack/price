from price.modules.tager.db_utils import (
    TagerContextDbu,
    # TagerBrandDbu,
    TagerBrandSynonymDbu,
    TagerBrandAssignmentDbu,
    TagerCategorySynonymDbu,
    TagerCategoryAssignmentDbu,
    # TagerColorDbu,
    TagerColorSynonymDbu,
    TagerTagSynonymDbu,
    TagerTaggingResultDbu,
)
from price.utils.rest_util import post
from price.modules.tager.tools import (
    clear_title,
    split_title,
    generate_similar_tag,
)

import logging
log = logging.getLogger(__name__)


class Services():
    def get_all_context(self):
        tcdbu = TagerContextDbu()
        return tcdbu.get_all_context()

    def add_tag_context(self, context):
        tcdbu = TagerContextDbu()
        log.info('Adding context {}'.format(context))
        context = context.strip().lower()
        return tcdbu.c_add_context(context)

    def add_brand_assignment(self, dict_tagging_product):
        tbs = TagerBrandSynonymDbu()
        assignment_brand = {}
        if dict_tagging_product is None:
            raise ValueError('No parameters')
        if dict_tagging_product.get('product_brand'):
            tager_brand_id = tbs.get_brand_id_by_synonym_name(dict_tagging_product.get('product_brand').lower())
            assignment_brand = {
                'imp_catalog_page_id': dict_tagging_product.get('imp_catalog_page_id'),
                'brand': dict_tagging_product.get('product_brand').lower(),
                'tager_brand_id': tager_brand_id
            }
        elif dict_tagging_product.get('catalog_brand'):
            tager_brand_id = tbs.get_brand_id_by_synonym_name(dict_tagging_product.get('catalog_brand').lower())
            assignment_brand = {
                'imp_catalog_page_id': dict_tagging_product.get('imp_catalog_page_id'),
                'brand': dict_tagging_product.get('catalog_brand').lower(),
                'tager_brand_id': tager_brand_id
            }
        else:
            temp = tbs.search_brnad(dict_tagging_product)
            log.info('Result tbs.search_brnad %r', temp)
            assignment_brand = {
                'imp_catalog_page_id': temp.imp_catalog_page_id,
                'brand': temp.brand,
                'tager_brand_id': temp.tager_brand_id
            }
        log.info('Assigment brand %r', assignment_brand)
        return assignment_brand

    def save_assignment_brand(self, assignment_brand):
        tba = TagerBrandAssignmentDbu()
        result = tba.c_add_assignment(
            assignment_brand.get('imp_catalog_page_id'),
            assignment_brand.get('brand'),
            assignment_brand.get('tager_brand_id')
        )
        url = 'http://127.0.0.1:7001/catalog_page_status'
        post(url, {
            'imp_catalog_page_id': assignment_brand.get('imp_catalog_page_id'),
            'status_type': 'brand'
            }
        )
        return result

    def add_brnad_synonym(self, value):
        tbs = TagerBrandSynonymDbu()
        log.info('Add brands synonym: {}'.format(value))
        result_dct = generate_similar_tag(value)
        """
        value = value.strip().lower()
        names = []
        names.append(value)
        for char in ['-', '_']:
            names.append(value.replace(' ', char))
            names.append('{}{}{}'.format(char, value.replace(' ', char), char))
            names.append('{}{}'.format(char, value.replace(' ', char)))
            names.append('{}{}'.format(value.replace(' ', char), char))
        """
        tbs.c_bulk_add_brnad(result_dct.get('names'))
        return result_dct.get('tag')

    def add_category_synonym(self, value):
        tbs = TagerCategorySynonymDbu()
        log.info('Add categorys synonym: {}'.format(value))
        result_dct = generate_similar_tag(value)
        """
        value = value.strip().lower()
        names = []
        names.append(value)
        for char in ['-', '_']:
            names.append(value.replace(' ', char))
            names.append('{}{}{}'.format(char, value.replace(' ', char), char))
            names.append('{}{}'.format(char, value.replace(' ', char)))
            names.append('{}{}'.format(value.replace(' ', char), char))
        """
        tbs.c_bulk_add_category(result_dct.get('names'))
        return result_dct.get('tag')

    def add_category_assignment(self, dict_tagging_product):
        tca = TagerCategoryAssignmentDbu()
        tcs = TagerCategorySynonymDbu()
        if dict_tagging_product is None:
            raise ValueError('No parameters')

        temp = tcs.search_category(dict_tagging_product)
        if temp:
            for element in temp:
                result = tca.c_add_assignment( # noqa F841
                    dict_tagging_product.get('imp_catalog_page_id'),
                    element[1],
                    element[2]
                )
            url = 'http://127.0.0.1:7001/catalog_page_status'
            post(url, {
                    'imp_catalog_page_id': dict_tagging_product.get('imp_catalog_page_id'),
                    'status_type': 'category'
                }
            )
        else:
            log.warning('Can\'t tagging category %r', dict_tagging_product.get('imp_catalog_page_id'))

    def add_color_synonym(self, value):
        tbs = TagerColorSynonymDbu()
        log.info('Add color synonym: {}'.format(value))
        """
        value = value.strip().lower()
        names = []
        names.append(value)
        for char in ['-', '_']:
            names.append(value.replace(' ', char))
            names.append('{}{}{}'.format(char, value.replace(' ', char), char))
            names.append('{}{}'.format(char, value.replace(' ', char)))
            names.append('{}{}'.format(value.replace(' ', char), char))
        """
        result_dct = generate_similar_tag(value)
        tbs.c_bulk_add_color(result_dct.get('names'))
        log.info('Result Dct %r)', result_dct)
        return result_dct.get('tag')

    def add_tag_synonym(self, context, value):
        tbs = TagerTagSynonymDbu()
        tc = TagerContextDbu()
        log.info('Add tag synonym: {} context: {}'.format(value, context))
        # value = value.strip().lower()
        tager_context_id = tc.get_context_by_name(context)
        result_dct = generate_similar_tag(value)
        """
        names = []
        names.append(value)
        for char in ['-', '_']:
            names.append(value.replace(' ', char))
            names.append('{}{}{}'.format(char, value.replace(' ', char), char))
            names.append('{}{}'.format(char, value.replace(' ', char)))
            names.append('{}{}'.format(value.replace(' ', char), char))
        """
        log.info('Dodaje tag {} context_id {}'.format(result_dct.get('names'), tager_context_id))
        tbs.c_bulk_add_tag(tager_context_id, result_dct.get('names'))
        return result_dct.get('tag')

    def tagging_product(self, imp_catalog_page_id, title):
        tba = TagerBrandAssignmentDbu()
        assignment_brand = tba.get_assignment(imp_catalog_page_id)
        if assignment_brand:
            ttr = TagerTaggingResultDbu()
            ch_title = clear_title(title)
            ch_title = self.remove_brand(imp_catalog_page_id, ch_title)
            ch_title = self.remove_category(imp_catalog_page_id, ch_title)
            ch_title = self.remove_color(imp_catalog_page_id, ch_title)
            ch_title = self.remove_tag(imp_catalog_page_id, ch_title)
            dct_tagging_result = {
                'name': split_title(ch_title),
                'imp_catalog_page_id': imp_catalog_page_id,
                'orginal_title': title,
                'brand': assignment_brand.brand
            }
            ttr.c_add_tagginig_result(dct_tagging_result)
        else:
            log.warning('For imp_catalog_page_id: {} title: "{}" no found brand'.format(imp_catalog_page_id, title))

    def get_list_results_by_string(self, string):
        ttr = TagerTaggingResultDbu()
        return ttr.get_list_results_by_string(string)

    def update_results_tags(self, tag):
        ttr = TagerTaggingResultDbu()
        return ttr.update_results_tags(tag)

    def remove_brand(self, imp_catalog_page_id, title):
        ttr = TagerTaggingResultDbu()
        result = ttr.search_brand_in_title(imp_catalog_page_id, title)
        for brand in result:
            title = title.replace(brand.value, '')
        return title.strip()

    def remove_category(self, imp_catalog_page_id, title):
        ttr = TagerTaggingResultDbu()
        result = ttr.search_category_in_title(imp_catalog_page_id, title)
        for category in result:
            title = title.replace(category.value, '')
        return title.strip()

    def remove_color(self, imp_catalog_page_id, title):
        ttr = TagerTaggingResultDbu()
        result = ttr.search_color_in_title(imp_catalog_page_id, title)
        for category in result:
            title = title.replace(category.value, '')
        return title.strip()

    def remove_tag(self, imp_catalog_page_id, title):
        ttr = TagerTaggingResultDbu()
        result = ttr.search_tag_in_title(imp_catalog_page_id, title)
        for category in result:
            title = title.replace(category.value, '')
        return title.strip()

    def get_product_by_id(self, imp_catalog_page_id):
        ttr = TagerTaggingResultDbu()
        return ttr.get_by_id(imp_catalog_page_id)

    def get_category_by_id(self, imp_catalog_page_id):
        tca = TagerCategoryAssignmentDbu()
        return tca.get_category_assignment(imp_catalog_page_id)
