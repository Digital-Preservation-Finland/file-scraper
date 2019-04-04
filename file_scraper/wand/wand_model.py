"""TODO"""

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class WandImageMeta(BaseMeta):
    """TODO"""

    _supported = {"image/png": [],
                  "image/jpeg": [],
                  "image/jp2": [],
                  "image/gif": []}
    _allow_versions = True

    def __init__(self, image):
        """TODO"""
        self._image = image

    @metadata()
    def index(self):
        """TODO"""
        return self._image.index

    @metadata()
    def mimetype(self):
        return self._image.container.mimetype

    @metadata()
    def version(self):
        """TODO"""
        return None

    @metadata()
    def stream_type(self):
        """TODO"""
        return "image"

    @metadata()
    def colorspace(self):
        """TODO"""
        if not self._image:
            return None
        return str(self._image.colorspace)

    @metadata()
    def width(self):
        """TODO"""
        if not self._image:
            return None
        return str(self._image.width)

    @metadata()
    def height(self):
        """TODO"""
        if not self._image:
            return None
        return str(self._image.height)

    @metadata()
    def bps_value(self):
        """TODO"""
        if not self._image:
            return None
        return str(self._image.depth)

    @metadata()
    def bps_unit(self):
        """TODO"""
        return None

    @metadata()
    def compression(self):
        """TODO"""
        if not self._image:
            return None
        return self._image.compression

    @metadata()
    def samples_per_pixel(self):
        return None


class WandTiffMeta(WandImageMeta):
    """TODO"""

    _supported = {"image/tiff": []}
    _allow_versions = True

    @metadata()
    def byte_order(self):
        """TODO"""
        if not self._image:
            return None

        for key, value in self._image.container.metadata.items():
            if key.startswith("tiff:endian"):
                if value == "msb":
                    return "big endian"
                elif value == "lsb":
                    return "little endian"

        return None
