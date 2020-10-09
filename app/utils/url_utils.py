import socket
import logging

log = logging.getLogger(__name__)


class UrlUtils():
    def __init__(self, url=None):
        if url is not None:
            self.url = url
            self.protocol = self.get_protocol(url)
            self.domain = self.get_domain(url)

    def get_protocol(self, url):
        tab = url.split('://')
        if len(tab) > 1 and tab[0] in ('http', 'https',):
            return tab[0]
        return None

    def get_domain(self, url):
        if url != '/':
            tab = url.split('://')
            if len(tab) > 1:
                return tab[1].split('/')[0]
        return False

    def is_correct_url(self, url):
        if self.get_domain(url) and self.get_protocol(url):
            return True
        else:
            return False

    def check_protocol(self, url):
        if self.get_protocol(url) in ['http', 'https']:
            return True
        return False

    def get_url_string(self, url):
        domain = self.get_domain(url)
        tab = url.split('//')
        result = tab[1].replace(domain, '')
        return result[1:]

    def get_attr_from_url(self, url):
        atributs = self.get_url_string(url).split('?')
        if len(atributs) >= 2:
            return atributs[1]
        return None

    def get_dicts_from_args(self, url):
        url_string = self.get_attr_from_url(url)
        new_dict = {}
        for var in url_string.split('&'):
            cos = var.split('=')
            new_dict[cos[0]] = cos[1]
        return new_dict

    def check_if_domain_exists(self, url):
        hostname = self.get_domain(url)
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.error:
            return False

    def is_page(self, url):
        if not url or url == '':
            return False
        if url[-3:] in ['htm', 'php'] or url[-4:] in ['html']:
            return True
        return False

    def is_image(self, url):
        if not url or url == '':
            return False
        if url[-3:] in ['jpg', 'png', 'gif']:
            return True
        return False

    def generate_link(self, link):
        if not link:
            return False
        domain = self.get_domain(link)
        if domain == self.domain:
            return link
        if domain is False and link[0:1] == '/':
            return self.protocol + '://' + self.domain + link
        return False
