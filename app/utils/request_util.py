import requests
import urllib.request as urllib2
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import logging

log = logging.getLogger(__name__)

class RequestUtil():
    def __init__(self):
        pass

    class Page():
        def __init__(self, req_obj):
            self.status_code = req_obj.status_code
            self.headers = req_obj.headers
            self.cookies = req_obj.cookies
            self.is_redirect = req_obj.is_redirect
            self.is_permanent_redirect = req_obj.is_permanent_redirect
            self.url = req_obj.url
            self.soup = BeautifulSoup(req_obj.content, features="html.parser")
            self.links = list(dict.fromkeys(self.get_list_links_from_page(self.soup)))
            self.image = list(dict.fromkeys(self.get_list_image_from_page(self.soup)))
            self.count_links = len(self.links)
            self.count_image = len(self.image)
            self.title = self.get_title(self.soup)

        def __repr__(self):
            return '<Page url:%r title: %s Links: %s [%s]>' %(self.url, self.title, self.count_links, self.status_code)

        def get_list_links_from_page(self, soup):
            if soup is None:
                return []
            return [
                    link.get("href")
                for link in soup.find_all("a")
            ]

        def get_list_image_from_page(self, soup):
            if soup is None:
                return []
            return [
                    image.get("src")
                for image in soup.find_all("img")
            ]

        def get_title(self, soup):
            if soup is None:
                return None
            return [
                title.text
                for title in soup.find_all("title")
            ][0]


    def add_header(self, req):
        req.add_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36')
        return req
    
    def download_page(self, url):
        log.info('I download page %r', url)
        r = requests.get(url)
        p = self.Page(r)
        return p

    def download_image(self, url):
        pass


