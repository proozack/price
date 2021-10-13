from app.utils.base_model import BaseModel


import logging
log = logging.getLogger(__name__)

class ProductPage(BaseModel):
    def __init__(self):
        self._category = NotImplemented
        self._description = NotImplemented
        self._title = NotImplemented
        self._size = NotImplemented
        self._brand = NotImplemented
        self._composition = NotImplemented
        self._color = NotImplemented
        self._attributes = NotImplemented
        self._images = NotImplemented
        self._active = True
        self._deleted = False
        self._imp_catalog_page_id = NotImplemented

    def __repr__(self):
        return '<DownloadedPage {} - {}>'.format(self.brand, self.title)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value):
        self._brand = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def size(self) -> list:
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def composition(self):
        return self._composition

    @composition.setter
    def composition(self, value):
        self._composition = value

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value): 
        self._images = value

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, value):
        self._deleted = value

    @property
    def imp_catalog_page_id(self):
        return self._imp_catalog_page_id

    @imp_catalog_page_id.setter
    def imp_catalog_page_id(self, value):
        self._imp_catalog_page_id = value

    def get_local_field_as_dict(self):
        return {
            '_category': self._category,
            '_description': self._description,
            '_title': self._title,
            '_size': self._size,
            '_brand': self._brand,
            '_composition': self._composition,
            '_color': self._color,
            '_attributes': self._attributes,
            '_images': self._images,
            '_active': self._active,
            '_deleted': self._deleted,
            '_imp_catalog_page_id': self._imp_catalog_page_id,
        }

