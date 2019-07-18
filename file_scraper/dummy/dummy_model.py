"""Metadata model for dummy scrapers."""
from __future__ import unicode_literals

from file_scraper.base import BaseMeta
from file_scraper.utils import metadata


class DummyMeta(BaseMeta):
    """Minimal metadata model for dummy scrapers."""

    def __init__(self, errors, mimetype=None, version=None):
        """
        Initialize the metadata model.

        :errors: A list in which the scraping errors are found.
        """
        self._errors = errors
        super(DummyMeta, self).__init__(mimetype, version)

    # pylint: disable=no-self-use
    @metadata()
    def stream_type(self):
        """Stream type is not known so return (:unav)."""
        return "(:unav)"
