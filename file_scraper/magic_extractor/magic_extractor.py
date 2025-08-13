"""Extractor for various binary and text file formats."""

import os

from file_scraper.magiclib import magiclib, magic_analyze, magiclib_version
from file_scraper.base import BaseExtractor
from file_scraper.magic_extractor.magic_model import (TextFileMagicMeta,
                                                      XmlFileMagicMeta,
                                                      XhtmlFileMagicMeta,
                                                      HtmlFileMagicMeta,
                                                      PdfFileMagicMeta,
                                                      OfficeFileMagicMeta,
                                                      PngFileMagicMeta,
                                                      JpegFileMagicMeta,
                                                      AiffFileMagicMeta,
                                                      Jp2FileMagicMeta,
                                                      TiffFileMagicMeta,
                                                      GifFileMagicMeta)


class MagicBaseExtractor(BaseExtractor):
    """Extractor for scraping files using magic."""

    _allow_unav_mime = False
    _supported_metadata = []

    @property
    def well_formed(self):
        """Magic is not able to check well-formedness.

        :returns: False if magic can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def _magic_call(self):
        """Fetch three values from file with using magic.
        These are: mimetype, info line (for version) and encoding.

        :returns: Python dict of the three fetched values from magic
        """
        MAGIC_LIB = magiclib()
        magicdict = {
            "magic_mime_type": MAGIC_LIB.MAGIC_MIME_TYPE,
            "magic_none": MAGIC_LIB.MAGIC_NONE,
            "magic_mime_encoding": MAGIC_LIB.MAGIC_MIME_ENCODING
        }

        magic_result = {}
        for key, value in magicdict.items():
            magic_result[key] = magic_analyze(MAGIC_LIB, value,
                                              self.filename)
        return magic_result

    def extract(self):
        """Populate streams with supported metadata objects."""
        if not os.path.exists(self.filename):
            self._errors.append("File not found.")
            return

        magic_result = self._magic_call()

        self.streams = list(self.iterate_models(
            magic_result=magic_result,
            pre_mimetype=self._predefined_mimetype))

        self._check_supported(allow_unav_mime=self._allow_unav_mime,
                              allow_unav_version=True,
                              allow_unap_version=True)
        self._messages.append("The file was analyzed successfully.")

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        return {"libmagic": {"version": magiclib_version()}}


class MagicTextExtractor(MagicBaseExtractor):
    """
    Magic extractor for text files.

    We have to allow (:unav) mimetype for text files, since we are not quite
    sure about the final mimetype. An XML file may also be plain text file.
    """
    _allow_unav_mime = True
    _supported_metadata = [TextFileMagicMeta, XmlFileMagicMeta,
                           XhtmlFileMagicMeta, HtmlFileMagicMeta]


class MagicBinaryExtractor(MagicBaseExtractor):
    """
    Magic extractor for binary files.

    Currently, these are all mime types which can not be anything else at the
    same time. Therefore it is pretty safe to disallow (:unav) as a mimetype
    result.
    """
    _supported_metadata = [PdfFileMagicMeta, OfficeFileMagicMeta,
                           PngFileMagicMeta, JpegFileMagicMeta,
                           Jp2FileMagicMeta, TiffFileMagicMeta,
                           GifFileMagicMeta, AiffFileMagicMeta]
