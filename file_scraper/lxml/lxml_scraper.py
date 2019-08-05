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

        # find out if parsing yielded results that are needed by the metadata
        # model
        try:
            tree.docinfo  # pylint: disable=pointless-statement
            tree_ok = True
        except AssertionError:
            tree_ok = False

        if tree_ok:
            for md_class in self._supported_metadata:
                self.streams.append(md_class(tree, self._given_mimetype,
                                             self._given_version))
            self._messages.append("Encoding metadata found.")
        else:
            self._errors.append("XML parsing failed: document information "
                                "could not be gathered.")

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
