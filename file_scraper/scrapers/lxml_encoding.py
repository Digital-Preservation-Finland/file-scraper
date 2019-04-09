"""Class for XML and HTML5 header encoding check with lxml. """

try:
    from lxml import etree
except ImportError:
    pass

from io import open
from file_scraper.base import BaseScraper
from file_scraper.utils import metadata


class XmlEncoding(BaseScraper):
    """Scrape character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {'text/xml': ['1.0'], 'text/html': ['5.0']}
    _only_wellformed = True  # Only well-formed check

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters: delimiter and separator
        """
        self.charset = None
        super(XmlEncoding, self).__init__(filename, mimetype,
                                          check_wellformed, params)

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
        if 'schematron' in params:
            return False
        if mimetype == 'text/xml' and check_wellformed:
            return True
        return super(XmlEncoding, cls).is_supported(mimetype, version,
                                                    check_wellformed, params)

    def scrape_file(self):
        """Scrape file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        file_ = open(self.filename, 'rb')
        tree = etree.parse(file_, parser)
        self.charset = tree.docinfo.encoding
        self.messages('Encoding metadata found.')
        self._check_supported()
        self._collect_elements()

    @metadata()
    def _charset(self):
        """Return charset."""
        return self.charset

    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'text'
