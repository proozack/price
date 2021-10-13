from celery import Celery
import time
import redis
from app.modules.imp_price.services import Services as PpServices 

import logging
log = logging.getLogger(__name__)

# from localconfig import CeleryApp as cfg
from app import create_app
app = create_app()
app.app_context().push()

app = Celery('tasks', broker='redis://192.168.254.201:6379/0')
app.conf.result_backend = 'redis://192.168.254.201:6379/1'

def connect():
    return redis.Redis(host="192.168.254.201", port=6379, db=10)

def counting(x, y):
    log.info('Startuje przetwarzanie dla parametrów x: %r y: %r', x, y)
    time.sleep(5)
    result = x * y
    r = connect()
    if r.get('suma'):
        wyn = int(r.get('suma').decode("utf-8"))
        r.set('suma', str(wyn + result))
    else:
        r.set('suma', str(result))
    log.info('Zapisuję nową sumę: %r', str(r.get('suma').decode("utf-8")))
    return result

@app.task
def add(x, y):
    log.info('Zlecam task dla danych x: %r y: %r', x, y)
    return counting(x, y)

@app.task
def product_page_parase(result):
    pps = PpServices()
    pps.process_product_pages(result)


