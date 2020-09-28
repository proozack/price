from typing import Callable, Any

class ValidationError(Exception):
    pass

def img_extension_validation(path_to_img: str) -> str:
    if path_to_img[-3:] in ['jpg','png','gif']:
        return path_to_img
    raise ValidationError('This path: "{}" isn\'t a path to image'.format(path_to_img))

def url_protocol_validation(url: str) -> str:
    tab = url.split('://')
    if len(tab) > 1 and tab[0] in ('http', 'https',):
        return url
    raise ValidationError('This string: "{}" isn\'t a correct url'.format(url))

#def customr_validation(validation_list: list[Callable], field_to_validation: Any) -> Any:
def custom_validation(validation_list: list, field_to_validation: Any) -> Any:
    for call_function in validation_list:
        field_to_validation =  call_function(field_to_validation)
    return field_to_validation

def is_www_img(http_resource: str) -> str:
    url_to_image_validation = [
        img_extension_validation,
        url_protocol_validation,
    ]
    return custom_validation(url_to_image_validation, http_resource)

def is_web_page(http_resource: str) -> str:
    page_validation = {
        url_protocol_validation,
    }
    return custom_validation(page_validation, http_resource)
