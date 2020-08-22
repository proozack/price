mport logging
from flask import g


log = logging.getLogger(__name__)


def dodaj_komunikat_rsp(komunikat, poziom=logging.INFO, exc_info=False):
    lst = getattr(g, 'komunikaty_rsp', None)
    if not lst:
        lst = []
        g.komunikaty_rsp = lst
    lst.append({
        'poziom': poziom,
        'tresc': komunikat,
    })
