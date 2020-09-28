from app.utils.base_model import BaseModel


import logging
log = logging.getLogger(__name__)


class Page(BaseModel):
    def __init__(self, parser, response, **kwargs):
        self._parser = parser
        self._parser.set_response(response)

        self._status_code = NotImplemented
        self._headers = NotImplemented
        self._cookies = NotImplemented
        self._is_redirect = NotImplemented
        self._is_permanent_redirect = NotImplemented
        self._url = NotImplemented
        # self._soup = NotImplemented
        self._links = NotImplemented
        self._image = NotImplemented
        self._entity = NotImplemented
        self._next_page = NotImplemented

        self._count_links = NotImplemented
        self._count_image = NotImplemented
        self._count_entity = NotImplemented

        self._title = NotImplemented

        self._set_links()
        self._set_image()
        self._set_entity()
        self._set_next_page()

    @property
    def status_code(self) -> str:
        return self._status_code

    @status_code.setter
    def status_code(self, value: str):
        self._status_code = value

    @property
    def headers(self) -> str:
        return self._headers

    @headers.setter
    def headers(self, value: str):
        self._headers = value

    @property
    def cookies(self) -> str:
        return self._cookies

    @cookies.setter
    def cookies(self, value: str):
        self._cookies = value

    @property
    def is_redirect(self) -> str:
        return self._is_redirect

    @is_redirect.setter
    def is_redirect(self, value: str):
        self._is_redirect = value

    @property
    def is_permanent_redirect(self) -> str:
        return self._is_permanent_redirect

    @is_permanent_redirect.setter
    def is_permanent_redirect(self, value: str):
        self._is_permanent_redirect = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    """
    @property
    def soup(self) -> str:
        return self._soup

    @soup.setter
    def soup(self, value: str):
        self._soup = value
    """

    @property
    def links(self) -> str:
        return self._links

    # @links.setter
    def _set_links(self) -> None:
        self._links = self._parser.get_list_links_from_page()
        self.count_links = len(self._links)

    @property
    def image(self) -> str:
        return self._image

    def _set_image(self) -> None:
        self._image = self._parser.get_list_image_from_page()
        self.count_links = len(self._image)

    @property
    def entity(self) -> str:
        return self._entity

    def _set_entity(self) -> None:
        self._entity = self._parser.get_entity()

    @property
    def count_links(self) -> str:
        return self._count_links

    @count_links.setter
    def count_links(self, value: str):
        self._count_links = value

    @property
    def count_image(self) -> str:
        return self._count_image

    @count_image.setter
    def count_image(self, value: str):
        self._count_image = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = self._parser.get_title()

    @property
    def next_page(self):
        return self._next_page

    def _set_next_page(self):
        self._next_page = self._parser.get_next_page()
