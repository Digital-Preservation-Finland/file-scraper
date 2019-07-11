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
        "application/msword": ["8.0", "8.5", "9.0", "10.0", "11.0"],
        "application/vnd.ms-excel": ["8.0", "9.0", "10.0", "11.0"],
        "application/vnd.ms-powerpoint": ["8.0", "9.0", "10.0", "11.0"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document": ["12.0", "14.0", "15.0"],
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet": ["12.0", "14.0", "15.0"],
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation": ["12.0", "14.0", "15.0"]}
    _allow_versions = True  # Allow any version
    _only_wellformed = True  # Only well-formed check

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
