from abc import ABC, abstractmethod
from typing import Callable, Any
from bs4 import BeautifulSoup



import logging

log = logging.getLogger(__name__)

class ParserError(Exception):
    pass

class AbstractParser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_response(self, value: str):
        pass

    @abstractmethod
    def get_list_links_from_page(self) -> list:
        pass

    @abstractmethod
    def get_list_image_from_page(self) -> list:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_entity(self) -> list:
        pass
