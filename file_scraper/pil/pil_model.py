"""Metadata model for image file formats scraped using PIL."""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata

try:
    import PIL.Image
except ImportError:
    pass


SAMPLES_PER_PIXEL = {"1": "1", "L": "1", "P": "1", "RGB": "3", "YCbCr": "3",
                     "LAB": "3", "HSV": "3", "RGBA": "4", "CMYK": "4",
                     "I": "1", "F": "1"}
SAMPLES_PER_PIXEL_TAG = 277


class BasePilMeta(BaseMeta):
    """Metadata model for image metadata."""

    def __init__(self, pil, index):
        """
        Initialize scraper.

        :pil: PIL image
        :index: Index of the current frame
        """
        self._pil = pil
        self._pil_index = index

    @metadata()
    def mimetype(self):
        return PIL.Image.MIME[self._pil.format]

    # pylint: disable=no-self-use
    @metadata()
    def version(self):
        """PIL does not know the version, return (:unav)."""
        return "(:unav)"

    @metadata()
    def stream_type(self):
        """Return stream type."""
        return "image"

    @metadata()
    def index(self):
        """Return stream index."""
        return self._pil_index

    @metadata()
    def colorspace(self):
        """Return colorspace."""
        return "(:unav)"

    @metadata()
    def width(self):
        """Return image width."""
        if self._pil.width is not None:
            return six.text_type(self._pil.width)
        return "(:unav)"

    @metadata()
    def height(self):
        """Return image height."""
        if self._pil is not None and \
                self._pil.height is not None:
            return six.text_type(self._pil.height)
        return "(:unav)"

    @metadata()
    def bps_value(self):
        """Return bits per sample."""
        return "(:unav)"

    @metadata()
    def bps_unit(self):
        """Return sample unit."""
        if self._pil is None:
            return "(:unav)"
        if self._pil.mode == "F":
            return "floating point"

        return "integer"

    @metadata()
    def compression(self):
        """Return compression scheme."""
        return "(:unav)"

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        return SAMPLES_PER_PIXEL[self._pil.mode]


class TiffPilMeta(BasePilMeta):
    """Metadata model for TIFF images."""

    _supported = {"image/tiff": []}  # Supported mimetype
    _allow_versions = True                # Allow any version

    @metadata()
    def width(self):
        """We will get width from another scraper."""
        return "(:unav)"

    @metadata()
    def height(self):
        """We will get height from another scraper."""
        return "(:unav)"

    @metadata()
    def colorspace(self):
        """We will get colorspace from another scraper."""
        return "(:unav)"

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        if self._pil is None:
            return "(:unav)"
        tag_info = self._pil.tag_v2
        if tag_info and SAMPLES_PER_PIXEL_TAG in tag_info.keys():
            return six.text_type(tag_info[SAMPLES_PER_PIXEL_TAG])
        return super(TiffPilMeta, self).samples_per_pixel()


class ImagePilMeta(BasePilMeta):
    """Collect image image metadata."""

    # Supported mimetypes
    _supported = {"image/png": [],
                  "image/gif": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return "(:unav)"

    @metadata()
    def height(self):
        """Return (:unav): we will get height from another scraper."""
        return "(:unav)"

    @metadata()
    def colorspace(self):
        """Return (:unav): we will get colorspace from another scraper."""
        return "(:unav)"


class Jp2PilMeta(BasePilMeta):
    """Collect JP2 image metadata."""

    # Supported mimetypes
    _supported = {"image/jp2": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        mime = super(Jp2PilMeta, self).mimetype()
        # Pillow 5.0.0 misidentifies JPEG2000
        if mime == "image/jpx":
            return "image/jp2"
        return mime

    @metadata()
    def version(self):
        if self.mimetype() == "image/jp2":
            return "(:unap)"
        return "(:unav)"

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return "(:unav)"

    @metadata()
    def height(self):
        """Return (:unav): we will get height from another scraper."""
        return "(:unav)"

    @metadata()
    def colorspace(self):
        """Return (:unav): we will get colorspace from another scraper."""
        return "(:unav)"


class JpegPilMeta(BasePilMeta):
    """Collect JPEG image metadata."""

    _supported = {"image/jpeg": []}  # Supported mimetypes
    _allow_versions = True  # Allow any version

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return "(:unav)"

    @metadata()
    def height(self):
        """Return (:unav): We will get height from another scraper."""
        return "(:unav)"

    @metadata()
    def colorspace(self):
        """Return (:unav): We will get colorspace from another scraper."""
        return "(:unav)"

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        exif_info = self._pil._getexif()  # pylint: disable=protected-access
        if exif_info and SAMPLES_PER_PIXEL_TAG in exif_info.keys():
            return six.text_type(exif_info[SAMPLES_PER_PIXEL_TAG])
        return super(JpegPilMeta, self).samples_per_pixel()
