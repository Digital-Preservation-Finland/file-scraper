"""Metadata models for Wand"""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class WandImageMeta(BaseMeta):
    """Metadata models for png, jp2 and gif files scraped with Wand"""
    # pylint: disable=no-self-use

    _supported = {"image/png": [],
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
        """
        If image exists, return its colorspace, otherwise return (:unav).
        """
        if not self._image:
            return UNAV
        colorspace = six.text_type(self._image.colorspace)
        if colorspace.lower() != "sRGB".lower():
            return colorspace

        # Further processing if sRGB was detected as colorspace.
        if colorspace.lower() in (self.icc_profile_name().lower(),):
            return colorspace
        # No valid reason to conclude the colorspace to be sRGB so returning
        # RGB.
        return "rgb"

    @metadata()
    def icc_profile_name(self):
        """Return ICC profile name if one is available.

        The name of the profile is same as the ICC description."""
        if not self._image:
            return UNAV
        return self._image.container.metadata.get("icc:description", UNAV)

    @metadata()
    def width(self):
        """If image exists, return its width, otherwise return (:unav)."""
        if not self._image:
            return UNAV
        return six.text_type(self._image.width)

    @metadata()
    def height(self):
        """If image exists, return its height, otherwise return (:unav)."""
        if not self._image:
            return UNAV
        return six.text_type(self._image.height)

    @metadata()
    def bps_value(self):
        """
        If image exists, return its colour depth, otherwise return (:unav).
        """
        if not self._image:
            return UNAV
        return six.text_type(self._image.depth)

    @metadata()
    def bps_unit(self):
        """Unit is always same, return (:unav)."""
        return UNAV

    @metadata()
    def compression(self):
        """Return the compression type if image exists, otherwise (:unav)."""
        if not self._image:
            return UNAV
        return self._image.compression

    @metadata()
    def samples_per_pixel(self):
        """
        Samples per pixel not available from this scraper, return (:unav).
        """
        return UNAV


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
            return UNAV

        for key, value in self._image.container.metadata.items():
            if key.startswith("tiff:endian"):
                if value == "msb":
                    return "big endian"
                elif value == "lsb":
                    return "little endian"

        raise ValueError("Unsupported byte order reported by Wand.")


class WandExifMeta(WandImageMeta):
    """Metadata models for JPEG files with EXIF metadata scraped with Wand"""

    _supported = {"image/jpeg": []}
    _allow_versions = True

    @metadata(important=True)
    def version(self):
        """Exif version in PRONOM registry form."""

        exif_version = self._image.container.metadata.get('exif:ExifVersion')
        if exif_version:
            return format_exif_version(exif_version)

        return UNAV


def format_exif_version(wand_exif_version):
    """Construct version numbering conforming to versions for Exchangeable
    Image File Format (Compressed) in PRONOM registry.

    Wand library extracts Exif version from metadata as a string. The string is
    in form of '48, 50, 50, 48' for 0220, 2.20 or 2.2 and is passed in that
    form to this format function. First two bytes form the major version
    number, third byte the minor and the last (optional) byte is the patch
    number of the version.

    :wand_exif_version: Version bytes string
    :return: Formatted version string

    """

    version_bytes = [chr(int(byte)) for byte in wand_exif_version.split(', ')]

    version_bytes[0] += version_bytes.pop(1)

    if version_bytes[-1] == '0':
        version_bytes.pop(-1)

    return '.'.join([str(int(version)) for version in version_bytes])
