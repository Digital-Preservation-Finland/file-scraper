"""Class for XML and HTML5 header encoding check with lxml. """
from __future__ import unicode_literals

try:
    from lxml import etree
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.lxml.lxml_model import LxmlMeta


class LxmlScraper(BaseScraper):
    """Scrape character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported_metadata = [LxmlMeta]
    _only_wellformed = True  # Only well-formed check

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """
        Return True if given MIME type and version are supported.

        This is not a Schematron scraper, we skip this in such case.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        :returns: True if scraper is supported
        """
        if params is None:
            params = {}
        if "schematron" in params:
            return False
        if mimetype == "text/xml" and check_wellformed:
            return True
        return super(LxmlScraper, cls).is_supported(mimetype, version,
                                                    check_wellformed, params)

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        with open(self.filename, "rb") as file_:
            tree = etree.parse(file_, parser)

        for md_class in self._supported_metadata:
            md_model = md_class(tree, self._given_mimetype,
                                self._given_version)

            # It is possible that for files that are not well-formed, trying
            # to use tree.docinfo causes an AssertionError. In that case we
            # shouldn't add a stream at all, but instead log an error. Only if
            # all metadata methods work normally, should the stream be added.
            try:
                for method in md_model.iterate_metadata_methods():
                    method()
            except AssertionError:
                self._errors.append("XML parsing failed: document "
                                    "information could not be gathered.")
            else:
                self.streams.append(md_model)

        # Only log success message if at least one metadata model was added to
        # streams
        if self.streams:
            self._messages.append("Encoding metadata found.")

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
