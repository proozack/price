import requests


import logging
log = logging.getLogger(__name__)


def post(url, data):
    log.info('Performs request {} data {}'.format(url, data))
    r = requests.post(url, data=data)
    log.info("Status Code %r", r.status_code)


def get(url):
    log.debug('Performs request {} '.format(url))
    r = requests.get(url)
    log.debug('Status Code {}'.format(r.status_code))
    return r.json()
