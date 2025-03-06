"""Metadata model for image file formats scraped using PIL."""

from copy import copy, deepcopy

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAP, UNAV
from file_scraper.utils import metadata

try:
    import PIL.Image
except ImportError:
    pass


SAMPLES_PER_PIXEL = {"1": "1", "L": "1", "P": "1", "RGB": "3", "YCbCr": "3",
                     "LAB": "3", "HSV": "3", "RGBA": "4", "CMYK": "4",
                     "I": "1", "F": "1", "LA": "2"}
SAMPLES_PER_PIXEL_TAG = 277


class BasePilMeta(BaseMeta):
    """Metadata model for image metadata."""

    def __init__(self, pil, index):
        """
        Initialize scraper. Copies metadata from PIL image frame to static
        variables.

        :pil: PIL image frame to extract metadata from
        :index: Index of the current frame

        """
        self._pil_index = index

        # Copy required data from PIL.Image to allow PilScraper to close
        # filehandle in PIL.Image. This allows scraping more than 1024 files in
        # one process (default max filehandle limt"

        self._pil_mimetype = PIL.Image.MIME[pil.format]
        self._pil_height = copy(getattr(pil, "height", UNAV))
        self._pil_width = copy(getattr(pil, "width", UNAV))
        self._pil_mode = copy(getattr(pil, "mode", UNAV))
        self._pil_tag_v2 = copy(getattr(pil, "tag_v2", UNAV))
        # pylint: disable=protected-access
        self._pil_getexif = None
        if hasattr(pil, "_getexif"):
            self._pil_getexif = deepcopy(pil._getexif())

    @metadata()
    def mimetype(self):
        return self._pil_mimetype

    # pylint: disable=no-self-use
    @metadata()
    def version(self):
        """PIL does not know the version, return (:unav)."""
        return UNAV

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
        return UNAV

    @metadata()
    def width(self):
        """Return image width."""
        return str(self._pil_width)

    @metadata()
    def height(self):
        """Return image height."""
        return str(self._pil_height)

    @metadata()
    def bps_value(self):
        """Return bits per sample."""
        return UNAV

    @metadata()
    def bps_unit(self):
        """Return sample unit."""

        if self._pil_mode == "F":
            return "floating point"

        return "integer"

    @metadata()
    def compression(self):
        """Return compression scheme."""
        return UNAV

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        return SAMPLES_PER_PIXEL[self._pil_mode]


class TiffPilMeta(BasePilMeta):
    """Metadata model for TIFF images."""

    _supported = {"image/tiff": []}  # Supported mimetype
    _allow_versions = True                # Allow any version

    @metadata()
    def width(self):
        """We will get width from another scraper."""
        return UNAV

    @metadata()
    def height(self):
        """We will get height from another scraper."""
        return UNAV

    @metadata()
    def colorspace(self):
        """We will get colorspace from another scraper."""
        return UNAV

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        tag_info = self._pil_tag_v2
        if tag_info and SAMPLES_PER_PIXEL_TAG in tag_info.keys():
            return str(tag_info[SAMPLES_PER_PIXEL_TAG])
        return super().samples_per_pixel()


class DngPilMeta(TiffPilMeta):
    """Metadata model for Dng images."""
    _supported = {"image/x-adobe-dng": []}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """Return mimetype."""
        return "image/x-adobe-dng"


class PngPilMeta(BasePilMeta):
    """Collect image image metadata."""

    # Supported mimetypes
    _supported = {"image/png": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return UNAV

    @metadata()
    def height(self):
        """Return (:unav): we will get height from another scraper."""
        return UNAV

    @metadata()
    def colorspace(self):
        """Return (:unav): we will get colorspace from another scraper."""
        return UNAV


class GifPilMeta(PngPilMeta):

    # Supported mimetypes
    _supported = {"image/gif": []}

    @metadata()
    def samples_per_pixel(self):
        """GIF is always a palette index image"""
        return "1" if self._pil_mode in SAMPLES_PER_PIXEL else UNAV


class Jp2PilMeta(BasePilMeta):
    """Collect JP2 image metadata."""

    # Supported mimetypes
    _supported = {"image/jp2": []}
    _allow_versions = True  # Allow any version

    @metadata()
    def mimetype(self):
        mime = super().mimetype()
        if mime == "image/jpx":
            return UNAV
        return mime

    @metadata()
    def version(self):
        if self.mimetype() == "image/jp2":
            return UNAP
        return UNAV

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return UNAV

    @metadata()
    def height(self):
        """Return (:unav): we will get height from another scraper."""
        return UNAV

    @metadata()
    def colorspace(self):
        """Return (:unav): we will get colorspace from another scraper."""
        return UNAV


class JpegPilMeta(BasePilMeta):
    """Collect JPEG image metadata."""

    _supported = {"image/jpeg": []}  # Supported mimetypes
    _allow_versions = True  # Allow any version

    @metadata()
    def width(self):
        """Return (:unav): we will get width from another scraper."""
        return UNAV

    @metadata()
    def height(self):
        """Return (:unav): We will get height from another scraper."""
        return UNAV

    @metadata()
    def colorspace(self):
        """Return (:unav): We will get colorspace from another scraper."""
        return UNAV

    @metadata()
    def samples_per_pixel(self):
        """Return samples per pixel."""
        exif_info = self._pil_getexif
        if exif_info and SAMPLES_PER_PIXEL_TAG in exif_info.keys():
            return str(exif_info[SAMPLES_PER_PIXEL_TAG])
        return super().samples_per_pixel()


class WebPMeta(BasePilMeta):
    """Metadata model for WebP images"""

    _supported = {"image/webp": []}
    _allow_versions = True

    @metadata()
    def mimetype(self):
        """Return mimetype"""
        return "image/webp"
