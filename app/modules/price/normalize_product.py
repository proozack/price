from app.utils.local_type import Ofert, TempProduct


import logging
log = logging.getLogger(__name__)

class NormalizeProduct():
    def __init__(self):
        pass

    def parse_offert(self, tp_object: TempProduct) -> TempProduct:
        tp_object = self._correct_currency(tp_object)
        return tp_object

    def _correct_currency(self, tp_object: TempProduct) -> TempProduct:
        currency = tp_object.currency
        if not currency:
            tp_object.currency = 'N/A'
        if currency.lower() in ['pln','zł','zl']:
            # setattr(tp_object, 'currency', 'zł')
            log.info('TP Object %r', tp_object.currency)
            tp_object.currency = 'zł'

        return tp_object
