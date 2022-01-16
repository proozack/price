import requests


import logging
log = logging.getLogger(__name__)


def post(url, data):
    log.info('Performs request {} data {}'.format(url, data))
    r = requests.post(url, data=data)
    log.info("Status Code %r", r.status_code)
