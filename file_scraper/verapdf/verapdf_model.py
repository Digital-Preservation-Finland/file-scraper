"""PDF/A metadata model."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class VerapdfMeta(BaseMeta):
    """Metadata model for PDF/A."""

    # Supported mimetypes and versions
    _supported = {"application/pdf": ["A-1a", "A-1b", "A-2a", "A-2b", "A-2u",
                                      "A-3a", "A-3b", "A-3u"]}

    def __init__(self, errors, profile):
        """
        Initialize the metadata model.

        :profile: profileName from verapdf report
        """
        self._errors = errors
        self._profile = profile

    @metadata()
    def mimetype(self):
        """Return mime type. File is PDF compliant without errors."""
        if not self._errors:
            return "application/pdf"
        return "(:unav)"

    @metadata(important=True)
    def version(self):
        """
        Return the version based on the profile given to the constructor.

        For files that are not PDF/A, other scrapers need to be used to
        determine the version.
        """
        if not self._errors and self._profile is not None:
            return "A" + self._profile.split("PDF/A")[1].split(
                " validation profile")[0].lower()
        return "(:unav)"

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
