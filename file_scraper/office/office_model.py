"""Metadata model for office file extractor."""

from file_scraper.base import BaseMeta


class OfficeMeta(BaseMeta):
    """Office file format extractor."""

    # Supported mimetypes and versions
    _supported = {
        "application/vnd.oasis.opendocument.text": ["1.0", "1.1", "1.2",
                                                    "1.3"],
        "application/vnd.oasis.opendocument.spreadsheet": [
            "1.0", "1.1", "1.2", "1.3"],
        "application/vnd.oasis.opendocument.presentation": [
            "1.0", "1.1", "1.2", "1.3"],
        "application/vnd.oasis.opendocument.graphics": ["1.0", "1.1", "1.2",
                                                        "1.3"],
        "application/vnd.oasis.opendocument.formula": ["1.0", "1.2", "1.3"],
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

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "binary"
