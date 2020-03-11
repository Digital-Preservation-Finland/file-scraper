"""Metadata models for Wand"""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class WandImageMeta(BaseMeta):
    """Metadata models for png, jpeg, jp2 and gif files scraped with Wand"""
    # pylint: disable=no-self-use

    _supported = {"image/png": [],
                  "image/jpeg": [],
                  "image/jp2": [],
                  "image/gif": []}
    _allow_versions = True

    def __init__(self, image):
        """
        Initialize the metadata model.

        :image: Wand SingleImage object for which the metadata is collected
        """
        self._image = image

    @metadata()
    def index(self):
        """Return the index of the SingleImage in its container."""
        return self._image.index

    @metadata()
    def mimetype(self):
        """Return the MIME type of the image."""
        return self._image.container.mimetype

    @metadata()
    def stream_type(self):
        """Wand is only used for images, so return "image"."""
        return "image"

    @metadata()
    def colorspace(self):
        """If image exists, return its colorspace, otherwise
           return (:unav).
        """
        if not self._image:
            return "(:unav)"
        return six.text_type(self._image.colorspace)

    @metadata()
    def width(self):
        """If image exists, return its width, otherwise return (:unav)."""
        if not self._image:
            return "(:unav)"
        return six.text_type(self._image.width)

    @metadata()
    def height(self):
        """Ig image exists, return its height, otherwise return (:unav)."""
        if not self._image:
            return "(:unav)"
        return six.text_type(self._image.height)

    @metadata()
    def bps_value(self):
        """If image exists, return its colour depth, otherwise
           return (:unav).
        """
        if not self._image:
            return "(:unav)"
        return six.text_type(self._image.depth)

    @metadata()
    def bps_unit(self):
        """Unit is always same, return (:unav)."""
        return "(:unav)"

    @metadata()
    def compression(self):
        """Return the compression type if image exists, otherwise (:unav)."""
        if not self._image:
            return "(:unav)"
        return self._image.compression

    @metadata()
    def samples_per_pixel(self):
        """Samples per pixel not available from this scraper,
           return (:unav).
        """
        return "(:unav)"


class WandTiffMeta(WandImageMeta):
    """Metadata models for tiff files scraped with Wand"""

    _supported = {"image/tiff": []}
    _allow_versions = True

    @metadata()
    def byte_order(self):
        """
        If image exists, return the byte order of the image, otherwise (:unav).

        :returns: "big endian" or "little endian" for existent images, (:unav)
                  if there is no image.
        :raises: ValueError if Wand reports a value other than "msb" or "lsb".
        """
        if not self._image:
            return "(:unav)"

        for key, value in self._image.container.metadata.items():
            if key.startswith("tiff:endian"):
                if value == "msb":
                    return "big endian"
                elif value == "lsb":
                    return "little endian"

        raise ValueError("Unsupported byte order reported by Wand.")
