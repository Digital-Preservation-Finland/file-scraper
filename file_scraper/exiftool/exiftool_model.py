""" """

from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import metadata


class ExifToolBaseMeta(BaseMeta):
    """
    Metadata models for files scraped with ExifTool.
    """
    def __init__(self, metadata):
        self._metadata = metadata

    @metadata()
    def mimetype(self):
        return self._metadata.get("File:MIMEType", UNAV)


class ExifToolDngMeta(ExifToolBaseMeta):
    """
    Metadata models for dng files scraped with ExifTool.
    """

    _supported = {"image/x-adobe-dng": ["1.3", "1.4", "1.5"]}
    _allow_versions = True

    @metadata(important=True)
    def mimetype(self):
        return super(ExifToolDngMeta, self).mimetype()

    @metadata(important=True)
    def version(self):
        if "EXIF:DNGVersion" in self._metadata:
            version = self._metadata["EXIF:DNGVersion"].replace(" ", ".")
            return version[:3]
        return UNAV

    @metadata()
    def byte_order(self):
        """
        Return the byte order of the image.

        :returns: "big endian or "little endian" for images, (:unav) if there
                   is no image.
        :raises: ValueError if ExifTool reports a value other than "MM" or
                 "II".
        """
        value = self._metadata.get("File:ExifByteOrder", UNAV)
        if value == "II":
            return "little endian"
        if value == "MM":
            return "big endian"
        raise ValueError("Unsupported byte order reported by ExifTool")

    @metadata()
    def samples_per_pixel(self):
        """ """
        return self._metadata.get("EXIF:SamplesPerPixel", UNAV)
