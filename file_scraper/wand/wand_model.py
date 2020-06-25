"""Metadata models for Wand"""
from __future__ import unicode_literals

import six

from file_scraper.base import BaseMeta
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
        """If image exists, return its height, otherwise return (:unav)."""
        if not self._image:
            return "(:unav)"
        return six.text_type(self._image.height)

    @metadata()
    def bps_value(self):
        """
        If image exists, return its colour depth, otherwise return (:unav).
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
        """
        Samples per pixel not available from this scraper, return (:unav).
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

        return "(:unav)"


def format_exif_version(wand_exif_version):
    """Construct version numbering conforming to versions for Exchangeable
    Image File Format (Compressed) in PRONOM registry.

    Wand library extracts Exif version from metadata as a string. The string is
    most often in form of '48, 50, 50, 48' for 0220, 2.20 or 2.2 and is passed
    in that form to this format function. First two bytes form the major
    version number, third byte the minor and the last (optional) byte is the
    patch number of the version.

    In certain situations, the Exif version may also be returned as a 4-digit
    ASCII string such as '0220'.

    :wand_exif_version: Version bytes string
    :return: Formatted version string

    """
    # ImageMagick versions prior to the commit
    # ac36bf9a08f058a259c902f7325b5b544f700994
    # may return the EXIF version as an ASCII string.
    # For example, instead of '48, 50, 50, 48' it may return '0220' instead

    if len(wand_exif_version) == 4 and wand_exif_version.isdigit():
        # Version string is a four-digit ASCII string
        major = str(int(wand_exif_version[0:2]))
        minor = wand_exif_version[2]
        patch = wand_exif_version[3]
        version_bytes = [major, minor]

        if patch != "0":
            version_bytes.append(version_bytes)

        return '.'.join(version_bytes)
    else:
        # Version string is a comma-separated list of integers mapping to
        # ASCII symbols
        version_bytes = [
            chr(int(byte)) for byte in wand_exif_version.split(', ')
        ]

        version_bytes[0] += version_bytes.pop(1)

        if version_bytes[-1] == '0':
            version_bytes.pop(-1)

        return '.'.join([str(int(version)) for version in version_bytes])
