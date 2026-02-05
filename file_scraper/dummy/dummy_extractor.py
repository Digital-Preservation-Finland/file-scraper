"""Dummy extractors."""
from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.dummy.dummy_model import (
    DetectedEpubVersionMeta,
    DetectedMimeVersionMeta,
    DetectedSiardVersionMeta,
    DetectedSpssVersionMeta,
    ExtractorNotFoundMeta,
)


class ExtractorNotFound(BaseExtractor):
    """Extractor for the case where extractor was not found."""

    # TODO: What is the point of this metadata model? Could Scraper
    # simply raise exception when extractor is not found? TPASPKT-1669

    def _extract(self):
        """No need to extract anything, just collect."""
        self._errors.append("Proper extractor was not found. "
                            "The file was not analyzed.")
        self.streams.append(
            ExtractorNotFoundMeta(
                mimetype=self._predefined_mimetype,
                version=self._predefined_version
            )
        )

    @property
    def well_formed(self):
        """
        Academically, well-formedness is not known and therefore result
        should be None. However, ExtractorNotFound should always be unwanted
        output, and therefore we return False.
        """
        return False

    def tools(self):
        return {}


class DetectedMimeVersionExtractor(BaseExtractor):
    """Dummy extractors scraping metadata and checking well-formedness.

    This extractor is needed because there is no extractors for file
    formats that are preserved only bit-level, but file-scraper still
    has to detect them. The purpose of this model is to:

    1. avoid using ExtractorNotFound extractor
    2. detect stream type of the file

    Support in metadata scraping and well-formedness checking.
    """

    # TODO: This extractor would be unnecessary if detectors would
    # extractors. See TPASPKT-1579.

    @property
    def well_formed(self):
        """Return well-formedness status of the extracted file.

        This extractor does not really extract the file. Therefore, None
        is returned as well-formedness, unless an error is found. True
        is never returned.

        None - Well-formedness is unknown
        False - File is not well-formed (errors found)
        """
        valid = super().well_formed
        if valid:
            return None
        return False

    def tools(self):
        return {}

    _supported_metadata = [
        DetectedMimeVersionMeta,
    ]

    _allow_unav_mime = False
    _allow_unav_version = True
    _allow_unap_version = True

    def _extract(self):
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


class DetectedMimeVersionMetadataExtractor(DetectedMimeVersionExtractor):
    """Dummy extractor for only scraping metadata.

    Some file formats are supported by proper extractors when
    well-formedness is checked, but they are not supported by any
    extractor when well-formedness is NOT checked. The purpose of this
    extractor is to:

    1. avoid using ExtractorNotFound extractor
    2. detect stream type of the file

    This extractor is used only only for metadata scraping, so it is not
    supported when well-formedness is checked.
    """

    _supported_metadata = [
        DetectedEpubVersionMeta,
        DetectedSpssVersionMeta,
        DetectedSiardVersionMeta,
    ]

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
        return super().is_supported(
            mimetype, version, check_wellformed, params)
