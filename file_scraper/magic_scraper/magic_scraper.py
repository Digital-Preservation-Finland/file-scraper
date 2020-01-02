"""Scraper for various binary and text file formats."""
from __future__ import unicode_literals

import os

from file_scraper.magiclib import magiclib, magic_analyze
from file_scraper.base import BaseScraper
from file_scraper.magic_scraper.magic_model import (BaseMagicMeta,
                                                    TextFileMagicMeta,
                                                    XmlFileMagicMeta,
                                                    XhtmlFileMagicMeta,
                                                    HtmlFileMagicMeta,
                                                    PdfFileMagicMeta,
                                                    OfficeFileMagicMeta,
                                                    ArcFileMagicMeta,
                                                    PngFileMagicMeta,
                                                    JpegFileMagicMeta,
                                                    Jp2FileMagicMeta,
                                                    TiffFileMagicMeta)

MAGIC_LIB = magiclib()


class MagicScraper(BaseScraper):
    """Scraper for scraping files using magic."""

    _supported_metadata = [TextFileMagicMeta, XmlFileMagicMeta,
                           XhtmlFileMagicMeta, HtmlFileMagicMeta,
                           PdfFileMagicMeta, OfficeFileMagicMeta,
                           ArcFileMagicMeta, PngFileMagicMeta,
                           JpegFileMagicMeta, Jp2FileMagicMeta,
                           TiffFileMagicMeta]

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
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        if not os.path.exists(self.filename):
            self._errors.append("File not found.")
            return

        magic_result = self._magic_call()

        self.iterate_models(magic_result=magic_result)

        self._check_supported(allow_unav_version=True, allow_unap_version=True)
        self._messages.append("The file was analyzed successfully.")
