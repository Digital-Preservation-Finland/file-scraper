"""Metadata models for Wand"""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV, UNAP
from file_scraper.metadata import metadata


class WandImageMeta(BaseMeta):
    """Metadata model for image files scraped with Wand"""

    _supported = {
        "image/gif": [],
        "image/jp2": [],
        "image/png": [],
        "image/x-adobe-dng": [],
    }
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
        colorspace = str(self._image.colorspace)
        if colorspace.lower() != "sRGB".lower():
            return colorspace

        # Further processing if sRGB was detected as colorspace based on
        # predetermined fields.
        if colorspace.lower() in self.icc_profile_name().lower():
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
        return str(self._image.width)

    @metadata()
    def height(self):
        """If image exists, return its height, otherwise return (:unav)."""
        if not self._image:
            return UNAV
        return str(self._image.height)

    @metadata()
    def bps_value(self):
        """
        If image exists, return its colour depth, otherwise return (:unav).
        """
        if not self._image:
            return UNAV
        return str(self._image.depth)

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
        Samples per pixel not available from this extractor, return (:unav).
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
                  if there is no image or if Wand reports a value other than
                  "msb" or "lsb".
        """
        if not self._image:
            return UNAV

        for key in self._image.container.metadata:
            if key.startswith("tiff:endian"):
                value = self._image.container.metadata[key]
                if value == "msb":
                    return "big endian"
                if value == "lsb":
                    return "little endian"
        return UNAV


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


class WandWebPMeta(WandImageMeta):
    """Metadata models for WebP files scraped with wand"""

    _supported = {"image/webp": []}
    _allow_versions = True

    @metadata(important=True)
    def compression(self):
        """Return compression quality if exists, otherwise (:unav)"""
        if self._image.compression_quality < 100:
            return "VP8 Lossy"
        if self._image.compression_quality == 100:
            return "VP8 Lossless"
        return UNAV

    @metadata(important=True)
    def version(self):
        """No version for WebP files, return (:unap)."""
        return UNAP


def format_exif_version(wand_exif_version):
    """Construct version numbering conforming to versions for Exchangeable
    Image File Format (Compressed) in PRONOM registry.

    Wand library extracts Exif version from metadata as a string. Depending
    on library version the resulted string is
        (1) in form of '48, 50, 50, 48' (in older ImageMagick), or
        (2) directly in form of '0220' (in newer ImageMagick)
    for 0220, 2.20 or 2.2 and is passed in that form to this format function.
    First two bytes form the major version number, third byte the minor and
    the last (optional) byte is the patch number of the version.

    :wand_exif_version: Version bytes string
    :return: Formatted version string

    """
    if len(wand_exif_version.split(", ")) == 4:
        version_bytes = [chr(int(byte)) for byte in
                         wand_exif_version.split(', ')]
    else:
        version_bytes = list(wand_exif_version)

    version_bytes[0] += version_bytes.pop(1)

    if version_bytes[-1] == '0':
        version_bytes.pop(-1)

    return '.'.join([str(int(version)) for version in version_bytes])
