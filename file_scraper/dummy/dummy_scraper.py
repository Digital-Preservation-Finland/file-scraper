"""Dummy scrapers."""
from __future__ import unicode_literals

import os.path

from file_scraper.base import BaseScraper
from file_scraper.defaults import UNAV
from file_scraper.utils import decode_path, generate_metadata_dict
from file_scraper.dummy.dummy_model import (
    DummyMeta, DetectedMimeVersionMeta, DetectedTextVersionMeta,
    DetectedSpssVersionMeta, DetectedPdfaVersionMeta
)

LOSE = (None, UNAV, "")


class ScraperNotFound(BaseScraper):
    """Scraper for the case where scraper was not found."""

    def scrape_file(self):
        """No need to scrape anything, just collect."""
        self._errors.append("Proper scraper was not found. "
                            "The file was not analyzed.")
        self.streams.append(DummyMeta())

    @property
    def well_formed(self):
        """
        Academically, well-formedness is not known and therefore result
        should be None. However, ScraperNotFound should always be unwanted
        output, and therefore we return False.
        """
        return False


class DummyScraper(BaseScraper):
    """Result None as well-formed, if there are no errors"""

    @property
    def well_formed(self):
        """
        Return False if there are errors, otherwise None.

        This is done as well-formedness of the file is not really known.
        """
        valid = super(DummyScraper, self).well_formed

        return None if valid else valid


class FileExists(DummyScraper):
    """Scraper for the case where file was not found."""

    def scrape_file(self):
        """Check if file exists."""
        if not self.filename:
            self._errors.append("No filename given.")
        elif os.path.isfile(self.filename):
            self._messages.append(
                "File {} was found.".format(decode_path(self.filename))
            )
        else:
            self._errors.append(
                "File {} does not exist.".format(decode_path(self.filename))
            )
        self.streams.append(DummyMeta())


class MimeMatchScraper(DummyScraper):
    """
    Scraper to check if the predefined mimetype and version match with the
    resulted ones.
    """

    _ALTERNATIVE_MIMETYPES = {
        "application/gzip": ["application/warc"]}
    _MIMES_UNAV_VERSIONS = [
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/vnd.oasis.opendocument.graphics",
        "application/vnd.oasis.opendocument.formula",
    ]
    _supported_metadata = [DummyMeta]

    def scrape_file(self):
        """
        No need to scrape anything, just compare already collected metadata.
        """
        mime = self._params.get("mimetype", UNAV)
        ver = self._params.get("version", UNAV)
        pre_list = self._ALTERNATIVE_MIMETYPES.get(
            self._predefined_mimetype, [])

        if mime == UNAV:
            self._errors.append("File format is not supported.")
        elif mime != self._predefined_mimetype and mime not in pre_list:
            self._errors.append(
                "Predefined mimetype '{}' and resulted mimetype '{}' "
                "mismatch.".format(self._predefined_mimetype, mime))

        if ver in [UNAV, None]:
            if mime in self._MIMES_UNAV_VERSIONS:
                self._messages.append(
                    "File format version can not be resolved for this file "
                    "format.")
            else:
                self._errors.append("File format version is not supported.")
        elif self._predefined_version not in [ver, None]:
            self._errors.append(
                "Predefined version '{}' and resulted version '{}' "
                "mismatch.".format(self._predefined_version, ver))

        self._messages.append("MIME type and file format version checked.")

        self.streams.append(DummyMeta())
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True,
                              allow_unap_version=True)


class DetectedMimeVersionScraper(DummyScraper):
    """
    Use the detected file format version for some file formats.
    Support in metadata scraping and well-formedness checking.
    """

    _supported_metadata = [DetectedMimeVersionMeta]

    def scrape_file(self):
        """
        Enrich the metadata with the detected file format version for some
        file formats.
        """
        mimetype = self._params.get("detected_mimetype",
                                    self._predefined_mimetype)
        version = self._params.get("detected_version", UNAV)
        self._messages.append("Using detected file format version.")
        self.streams = list(self.iterate_models(mimetype=mimetype,
                                                version=version))
        self._check_supported(allow_unav_mime=False, allow_unav_version=True,
                              allow_unap_version=True)


class DetectedMimeVersionMetadataScraper(DetectedMimeVersionScraper):
    """
    Variation of DetectedMimeVersionScraper for SPSS Portable, text and PDF
    files. Support only in metadata scraping.
    """

    _supported_metadata = [DetectedSpssVersionMeta,
                           DetectedTextVersionMeta,
                           DetectedPdfaVersionMeta]

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Support only when no checking of well-formedness is done.

        :mimetype: MIME type of a file
        :version: Version of a file. Defaults to None.
        :check_wellformed: True for scraping with well-formedness check, False
                           for skipping the check. Defaults to True.
        :params: None
        :returns: True if the MIME type and version are supported, False if not
        """
        if check_wellformed:
            return False
        return super(DetectedMimeVersionMetadataScraper, cls).is_supported(
            mimetype, version, check_wellformed, params)


class ResultsMergeScraper(DummyScraper):
    """
    Scraper to merge the scraper results and handle possible conflicts
    between the scraper tools.
    """

    _supported_metadata = [DummyMeta]

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        """
        super(ResultsMergeScraper, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)
        if params is None:
            params = {}
        self._scraper_results = params.get("scraper_results", None)

    def scrape_file(self):
        """
        No need to scrape anything, just merge already collected metadata.
        """
        streams, conflicts = generate_metadata_dict(
            self._scraper_results, LOSE)
        self.streams = streams
        for error_message in conflicts:
            self._errors.append(error_message)
        self._messages.append("Scraper results merged into streams")
