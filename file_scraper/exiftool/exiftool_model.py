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
        if "File:MIMEType" in self._metadata:
            return self._metadata["File:MIMEType"]
        return UNAV


class ExifToolDngMeta(ExifToolBaseMeta):
    """
    Metadata models for dng files scraped with ExifTool.
    """

    _supported = {"image/x-adobe-dng": ["1.3.0.0", "1.4.0.0", "1.5.0.0"]}

    @metadata(important=True)
    def mimetype(self):
        return super(ExifToolDngMeta, self).mimetype()

    @metadata(important=True)
    def version(self):
        if "EXIF:DNGVersion" in self._metadata:
            return self._metadata["EXIF:DNGVersion"].replace(" ", ".")
        return UNAV

    @metadata()
    def stream_type(self):
        return "image"


class ExifToolTiffDngMeta(ExifToolDngMeta):
    """

    """
    _supported = {"image/tiff": []}
    _allow_versions = True
