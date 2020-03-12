"""Scraper for various binary and text file formats."""
from __future__ import unicode_literals

import os

from file_scraper.magiclib import magiclib, magic_analyze
from file_scraper.base import BaseScraper
from file_scraper.magic_scraper.magic_model import (TextFileMagicMeta,
                                                    XmlFileMagicMeta,
                                                    XhtmlFileMagicMeta,
                                                    HtmlFileMagicMeta,
                                                    PdfFileMagicMeta,
                                                    OfficeFileMagicMeta,
                                                    ArcFileMagicMeta,
                                                    PngFileMagicMeta,
                                                    JpegFileMagicMeta,
                                                    Jp2FileMagicMeta,
                                                    TiffFileMagicMeta,
                                                    GifFileMagicMeta,
                                                    WarcFileMagicMeta)

MAGIC_LIB = magiclib()


class MagicBaseScraper(BaseScraper):
    """Scraper for scraping files using magic."""

    _allow_unav_mime = False
    _supported_metadata = []

    def _magic_call(self):
        """Fetch three values from file with using magic.
        These are: mimetype, info line (for version) and encoding.

        :returns: Python dict of the three fetched values from magic
        """
        magicdict = {
            "magic_mime_type": MAGIC_LIB.MAGIC_MIME_TYPE,
            "magic_none": MAGIC_LIB.MAGIC_NONE,
            "magic_mime_encoding": MAGIC_LIB.MAGIC_MIME_ENCODING
        }

        magic_result = {}
        for key in magicdict:
            magic_result[key] = magic_analyze(MAGIC_LIB, magicdict[key],
                                              self.filename)
        return magic_result

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not os.path.exists(self.filename):
            self._errors.append("File not found.")
            return

        magic_result = self._magic_call()

        self.iterate_models(magic_result=magic_result,
                            pre_mimetype=self._predefined_mimetype)

        self._check_supported(allow_unav_mime=self._allow_unav_mime,
                              allow_unav_version=True,
                              allow_unap_version=True)
        self._messages.append("The file was analyzed successfully.")


class MagicTextScraper(MagicBaseScraper):
    """
    Magic scraper for text files.

    We have to allow (:unav) mimetype for text files, since we are not quite
    sure about the final mimetype. An XML file may also be plain text file.
    """
    _allow_unav_mime = True
    _supported_metadata = [TextFileMagicMeta, XmlFileMagicMeta,
                           XhtmlFileMagicMeta, HtmlFileMagicMeta]


class MagicBinaryScraper(MagicBaseScraper):
    """
    Magic scraper for binary files.

    Currently, these are all mime types which can not be anything else at the
    same time. Therefore it is pretty safe to disallow (:unav) as a mimetype
    result.
    """
    _supported_metadata = [PdfFileMagicMeta, OfficeFileMagicMeta,
                           ArcFileMagicMeta, PngFileMagicMeta,
                           JpegFileMagicMeta, Jp2FileMagicMeta,
                           TiffFileMagicMeta, GifFileMagicMeta,
                           WarcFileMagicMeta]
