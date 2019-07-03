"""Scraper for various binary and text file formats."""

import os

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


class MagicScraper(BaseScraper):
    """Scraper for scraping files using magic."""

    _supported_metadata = [TextFileMagicMeta, XmlFileMagicMeta,
                           XhtmlFileMagicMeta, HtmlFileMagicMeta,
                           PdfFileMagicMeta, OfficeFileMagicMeta,
                           ArcFileMagicMeta, PngFileMagicMeta,
                           JpegFileMagicMeta, Jp2FileMagicMeta,
                           TiffFileMagicMeta]

    def scrape_file(self):
        """Populate streams with supported metadata objects."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return

        if "mimetype" not in self._params:
            raise AttributeError("MagicScraper was not given a parameter "
                                 "dict containing mimetype of the file.")

        if not os.path.exists(self.filename):
            self._errors.append("File not found.")
            return

        mimefinder = BaseMagicMeta(self.filename, self._errors)
        mimetype = mimefinder.mimetype()
        mimetype_guess = self._params["mimetype"]

        if not self.is_supported(mimetype):
            self._errors.append("Unsupported MIME type %s" % mimetype)
            return

        if mimetype == "text/xml":
            if mimetype_guess == "text/xml":
                self.streams.append(XmlFileMagicMeta(self.filename,
                                                     self._errors))
            elif mimetype_guess == "application/xhtml+xml":
                self.streams.append(XhtmlFileMagicMeta(self.filename,
                                                       self._errors))
            else:
                self._errors.append("MIME type %s given to MagicScraper does "
                                    "not match %s obtained by the scraper." % (
                                        mimetype_guess, mimetype))
                return
        else:
            for md_class in self._supported_metadata:
                if not md_class.is_supported(mimetype):
                    continue
                self.streams.append(md_class(self.filename, self._errors))

        self._check_supported(allow_unav_version=True, allow_unap_version=True)
        self._messages.append("The file was analyzed successfully.")
