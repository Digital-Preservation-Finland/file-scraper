"""Class for XML and HTML5 header encoding check with lxml. """
from __future__ import unicode_literals

try:
    from lxml import etree
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.lxml_scraper.lxml_model import LxmlMeta


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

        # It is possible that for files that are not well-formed, trying
        # to use tree.docinfo causes an AssertionError.
        #
        # The except catches all exceptions, because AssertionError from
        # the compiled cython module is otherwise not caught by all python
        # versions.
        try:
            encoding = tree.docinfo.encoding
            if not self._params.get("charset", None):
                self._errors.append("Character encoding not defined.")
            elif encoding is not None and \
                    encoding.upper() != self._params["charset"]:
                self._errors.append(
                    "Found encoding declaration %s from the file %s, but %s "
                    "was expected." % (encoding, self.filename,
                                       self._params["charset"]))
        except Exception:  # pylint: disable=broad-except
            self._errors.append("XML parsing failed: document "
                                "information could not be gathered.")

        for md_class in self._supported_metadata:
            self.streams.append(md_class(self._given_mimetype,
                                         self._given_version))

        # Only log success message if we have no errors
        if not self._errors:
            self._messages.append("Encoding metadata found.")

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)
