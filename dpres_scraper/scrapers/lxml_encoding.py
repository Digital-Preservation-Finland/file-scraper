"""class for XML and HTML5 header encoding check with lxml. """
try:
    from lxml import etree
except ImportError:
    pass

from dpres_scraper.base import BaseScraper


class XmlEncoding(BaseScraper):
    """
    Character encoding validator for HTML5 and XML files
    """

    # We use JHOVE for HTML4 and XHTML files.
    _supported = {'text/xml': [], 'text/html': ['5.0']}
    _only_wellformed = True

    def __init__(self, mimetype, filename, validation):
        """
        """
        self._charset = None
        super(XmlEncoding, self).__init__(mimetype, filename, validation)

    def scrape_file(self):
        """Scrape file
        """
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        fd = open(self.filename)
        tree = etree.parse(fd, parser)
        self._charset = tree.docinfo.encoding
        self.messages('Encoding metadata match found.')
        self._collect_elements()

    def _s_charset(self):
        """Return charset
        """
        return self._charset

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'char'
