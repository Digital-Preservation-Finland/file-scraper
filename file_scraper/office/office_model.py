"""Metadata model for office file scraper."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class OfficeMeta(BaseMeta):
    """Office file format scraper."""

    # Supported mimetypes and versions
    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.spreadsheet": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.presentation": [
            "1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2"],
        "application/msword": ["97-2003"],
        "application/vnd.ms-excel": ["8X"],
        "application/vnd.ms-powerpoint": ["97-2003"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": ["2007 onwards"],
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet": ["2007 onwards"],
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": ["2007 onwards"]}
    _allow_versions = True  # Allow any version
    _only_wellformed = True  # Only well-formed check

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
