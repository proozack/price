import requests
from app.utils.url_utils import UrlUtils


class SmallResponseObject():

    def __init__(self, url: str, contents: str, status_code: str):
        self._url = url
        uu = UrlUtils(url)
        self._status_code = status_code

        self._domain = uu.domain
        self._protocol = uu.protocol

        if status_code != '404':
            self._contents = contents

    @property
    def url(self):
        return self._url

    @property
    def clear_url(self):
        return '{}://{}'.format(self._protocol, self._domain)

    @property
    def domain(self):
        return self._domain

    @property
    def protocol(self):
        return self._protocol

    def get_status_code(self) -> int:
        return self._status_code

    def get_contents(self) -> str:
        return self._contents

    def __repr__(self):
        return '<SmallResponseObject url="{}" status:"{}">'.format(self._url, self._status_code)


def standard_request(url: str) -> SmallResponseObject:
    r = requests.get(url)
    return SmallResponseObject(url, r.content, r.status_code)
