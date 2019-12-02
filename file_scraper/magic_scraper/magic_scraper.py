"""Scraper for various binary and text file formats."""
from __future__ import unicode_literals

import os
import six

from file_scraper.utils import encode_path
from file_scraper.magiclib import magiclib
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

        :returns: dict of the three fetched values 
        """
        magicdict = {
            "magic_mime_type": MAGIC_LIB.MAGIC_MIME_TYPE,
            "magic_none": MAGIC_LIB.MAGIC_NONE,
            "magic_mime_encoding": MAGIC_LIB.MAGIC_MIME_ENCODING
        }

        magic_values = {}
        for key in magicdict:
            try:
                magic_ = MAGIC_LIB.open(magicdict[key])
                magic_.load()
                magic_values[key] = magic_.file(encode_path(self.filename))
            except Exception as exception:  # pylint: disable=broad-except
                self._errors.append("Error in analysing file")
                self._errors.append(six.text_type(exception))
                magic_values[key] = None
            finally:
                magic_.close()

        return magic_values

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        if "mimetype_guess" not in self._params:
            raise AttributeError("MagicScraper was not given a parameter "
                                 "dict containing key 'mimetype_guess'.")

        if not os.path.exists(self.filename):
            self._errors.append("File not found.")
            return

        magic_values = self._magic_call()
        mimefinder = BaseMagicMeta(magic_values=magic_values,
                                   mimetype=self._given_mimetype,
                                   version=self._given_version)
        mimetype = mimefinder.mimetype()
        mimetype_guess = self._params["mimetype_guess"]

        if not self.is_supported(mimetype):
            self._errors.append("Unsupported MIME type %s" % mimetype)
            return

        if mimetype == "text/xml":
            if mimetype_guess == "text/xml":
                self.streams.append(XmlFileMagicMeta(magic_values))
            elif mimetype_guess == "application/xhtml+xml":
                self.streams.append(XhtmlFileMagicMeta(magic_values))
            else:
                self._errors.append("MIME type %s given to MagicScraper does "
                                    "not match %s obtained by the scraper." % (
                                        mimetype_guess, mimetype))
                return
        else:
            for md_class in self._supported_metadata:
                if not md_class.is_supported(mimetype):
                    continue
                self.streams.append(md_class(magic_values=magic_values,
                                             mimetype=self._given_mimetype,
                                             version=self._given_version))

        self._check_supported(allow_unav_version=True, allow_unap_version=True)
        self._messages.append("The file was analyzed successfully.")
