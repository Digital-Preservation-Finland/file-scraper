"""PDF/A metadata model."""

from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.metadata import metadata


class VerapdfMeta(BaseMeta):
    """Metadata model for PDF/A."""

    # Supported mimetypes and versions
    _supported = {"application/pdf": ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u",
                                      "A-3a", "A-3b", "A-3u"]}

    def __init__(self, well_formed, profile):
        """
        Initialize the metadata model.

        :well_formed: Well-formed status from extractor
        :profile: profileName from verapdf report
        """
        self._well_formed = well_formed
        self._profile = profile

    @metadata()
    def mimetype(self):
        """
        Return mime type.

        If the well-formed status from extractor is False,
        then we do not know the actual MIME type.
        """
        return "application/pdf" if self._well_formed else UNAV

    @metadata(important=True)
    def version(self):
        """
        Return the version based on the profile given to the constructor.

        For files that are not PDF/A, other extractors need to be used to
        determine the version.

        If the well-formed status from extractor is False,
        then we do not know the actual version.
        """
        if self._well_formed and self._profile is not None:
            return "A" + self._profile.split("PDF/A")[1].split(
                " validation profile")[0].lower()
        return UNAV

    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
