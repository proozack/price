from PIL import Image as Img
from . import local_type as lt
from . import file_utils as fu
import imagehash
import requests
from colorthief import ColorThief

import logging
log = logging.getLogger(__name__)


class ImageUtils():
    def __init__(self, local_path):
        self._i = Img.open(local_path)
        self._size = len(self._i.fp.read())
        self._hash = imagehash.average_hash(self._i)
        self.color_thief = ColorThief(local_path)

    def set_image(self, local_path):
        self._i = Img.open(local_path)
        self._size = len(self._i.fp.read())
        self._hash = imagehash.average_hash(self._i)

    @property
    def image(self) -> Img:
        return self._i

    @property
    def dimension(self) -> lt.Dimension:
        w, h = self._i.size
        return lt.Dimension(w, h, self._i.getbands())

    @property
    def size(self) -> int:
        """
        return file size in byte
        """
        return self._size

    @property
    def hash(self):
        return self._hash

    @property
    def orientation(self) -> str:
        if self.dimension.height > self.dimension.width:
            return 'vertical'
        return 'horizontal'

    @property
    def main_color(self) -> str:
        try:
            return self.color_thief.get_color(quality=1)
        except Exception:
            log.warn('Can\'t get color from image')
            return None

    @property
    def get_contol_sum(self) -> str:
        return str(self.hash)


class WebImageUtils(ImageUtils):
    def __init__(self, url_to_image):
        with fu.ctx_tmp_dir() as f:
            r = requests.get(url_to_image)
            if r.status_code == 200:
                path = fu.utworz_tmp_plik(f, r.content)
                super().__init__(path)
            else:
                log.warn('Download error {}'.format(r.status_code))
