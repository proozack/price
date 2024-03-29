from sqlalchemy import and_
from sqlalchemy import cast, Date
from sqlalchemy.sql.expression import func
from price import db
from price.modules.price.models import Image, Ofert
from price.utils.image_utils import WebImageUtils

import logging
log = logging.getLogger(__name__)


class EnrichImage():
    def set_url_image(self, url_iamge):
        self.url_to_file = url_iamge

    def is_url_in_db(self):
        result = Image.query.filter(Image.image == self.url_to_file).first()
        return result

    def process_image(self):
        self.w = WebImageUtils(self.url_to_file)
        i = Image()
        i.control_sum = self.w.get_contol_sum
        i.image = self.url_to_file
        i.dimension = self.w.dimension
        i.size = self.w.size
        i.orientation = self.w.orientation
        i.created_by = 1
        i.main_color = self.w.main_color
        db.session.add(i)
        db.session.commit()
        return i

    def add_image(self, url_iamge):
        self.set_url_image(url_iamge)
        if not self.is_url_in_db():
            try:
                self.process_image()
                return True
            except:
                log.info('Image %r is wrong: ', url_iamge)
                return False
        return False


class EnrichImages(EnrichImage):
    def __init__(self):
        pass

    def parase_all_images(self):
        # oferts = Ofert.query.all()
        oferts = db.session.query(
                Ofert.image
            ).outerjoin(
                Image,
                Ofert.image == Image.image
            ).filter(
                and_(
                    Image.id == None, # noqa E711
                    Ofert.image.isnot(None),
                    Ofert.creation_date.cast(Date) == func.current_date()
                )
            )
        for lp, o in enumerate(oferts):
            log.info('{} -> {} '.format(lp, o.image))
            self.add_image(o.image)
