import pprint

import logging
log = logging.getLogger(__name__)


def div_catalogs_parser(_soup):
    count_dict = {}
    # szukam wszystkich divów (każda współczena strona jest oparta na divach
    for field in _soup.find_all('div'):
        # szukam atrybutu class dla div
        tmp = field.attrs.get('class')
        if tmp is None:
            continue
        # jeżeli div ma kilka klass używam zanku @ do łączenia ich ze sobą tworząc unikatowy klucz
        key = '@'.join(tmp)
        if count_dict.get(key):
            count_dict[key] = count_dict[key] + 1
        else:
            count_dict[key] = 1
        # log.info('to jest atrs firled %r', key)

    # grupuje klasy po ilości wystąpień i nie biorę pod uwagę takich które występują jedne raz 
    count_dict = {
        key: value
        for key, value in count_dict.items() if value != 1
    }
    # log.info('To jest słownik\n: %r', pprint.pprint(count_dict)) 
    

    sdict = {
        'counter': 1,
        'class': []
    }

    result_dict = {}
    # przetwarzam słownik tak aby kluczem był ilośc wystąpień a pola to lista nazw klas i ilosc klas
    for key, value in count_dict.items():
        if result_dict.get(value):
            result_dict[value]['counter'] = result_dict.get(value)['counter'] + 1
            result_dict[value]['class'].append(key)

        else:
            result_dict[value] = {
                'counter': 1,
                'class': []
            }

            result_dict[value]['class'].append(key)

    # log.info('To jest słownik\n: %r', pprint.pprint(result_dict)) 
   
    max_key = 0
    for key, value in result_dict.items():
        if value.get('counter') != 1:
            # log.info('Key %r -> Value: %r ', key, value)
            if  key > max_key:
                max_key = key


    cos = result_dict.get(max_key)
    # log.info('To jest właściwy wynik\nklucz: %r\nvalue: %r', max_key, cos)
    # log.info('To jest wylosowana klasa: %r', cos.get('class')[0])
    wylosowana_klasa = cos.get('class')[0]
    wylosowana_klasa = wylosowana_klasa.split('@')[0]

    for result in _soup.findAll('div', {"class" : wylosowana_klasa}):
        # log.info('Oferta: \n %r\n', result)
        # log.info('-----------------------------------------------------------')
        yield result


def article_catalogs_parser(_soup):
    # log.info('Tutaj')
    for field in _soup.find_all('article'):
        #log.info('To jest oferta: \n%r\n', field)
        #log.info('-----------------------------------------------------------')
        yield field

def div_class_row_parser(_soup):
    for field in _soup.find_all(attrs={"class" : "cp-list"}):
        yield field

def div_row_parser(_soup):
    for field in _soup.find_all('li'):
        yield field

def figure_row_parser(_soup):
    for field in _soup.find_all('figure'):
        yield field

def div_kat_prod_parser(_soup):
    for field in _soup.find_all(attrs={"class" : "kat_prod"}):
        yield field

def div_product_parser(_soup):
    for field in _soup.find_all(attrs={"class" : "product"}):
        yield field

def div_item_product(_soup):
    for field in _soup.find_all(attrs={"class" : "item"}):
        yield field

def div_product_box_parser(_soup):
    for field in _soup.find_all(attrs={"class" : "product-box"}):
        yield field

def div_multi_class(_soup):
    for field in _soup.find_all(attrs={"class" : "product-one"}):
        yield field

def catalogs_parser_wrapper(parser_type, soup):
    parsers_type_method = {
        'div': div_catalogs_parser,
        'article': article_catalogs_parser,
        'div_row': div_class_row_parser,
        'div_li': div_row_parser,
        'figure': figure_row_parser,
        'div_kat_prod': div_kat_prod_parser,
        'div_product': div_product_parser,
        'div_item_product': div_item_product,
        'div_product_box': div_product_box_parser,
        'div_multi_class': div_multi_class,
    }
    for field in parsers_type_method[parser_type](soup):
        yield field
