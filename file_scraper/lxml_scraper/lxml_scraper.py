"""Class for XML and HTML5 header encoding check with lxml. """
from __future__ import unicode_literals

try:
    from lxml import etree
except ImportError:
    pass

import six

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
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True)
        with open(self.filename, "rb") as file_:
            try:
                tree = etree.parse(file_, parser)
            except etree.XMLSyntaxError as exception:
                self._errors.append("Failed: document is not well-formed.")
                self._errors.append(six.text_type(exception))
                return
            except IOError as exception:
                self._errors.append("Failed: missing file.")
                self._errors.append(six.text_type(exception))
                return

        self.streams = list(self.iterate_models(tree=tree))

        # Only log success message if at least one metadata model was added to
        # streams. Check that it corresponds to given charset.
        if self.streams:
            self._messages.append("Encoding metadata found.")
            if not self._params.get("charset", None):
                self._errors.append("Character encoding not defined.")
                return
            encoding = self.streams[0].charset()
            if encoding is not None and \
                    encoding.upper() != self._params["charset"]:
                self._errors.append(
                    "Found encoding declaration %s from the file %s, but %s "
                    "was expected." % (encoding, self.filename,
                                       self._params["charset"]))

        self._check_supported(allow_unav_mime=True, allow_unav_version=True)

    def iterate_models(self, **kwargs):
        """
        Iterate metadata models.

        It is possible that for files that are not well-formed, trying
        to use tree.docinfo causes an AssertionError. In that case we
        shouldn't add a stream at all, but instead log an error. Only if
        all metadata methods work normally, should the stream be added.

        The except catches all exceptions, because AssertionError from
        the compiled cython module is otherwise not caught by all python
        versions.

        :kwargs: Model specific parameters
        """
        for md_class in self._supported_metadata:

            if md_class.is_supported(self._predefined_mimetype,
                                     self._predefined_version,
                                     self._params):

                md_model = md_class(**kwargs)
                try:
                    for method in md_model.iterate_metadata_methods():
                        method()
                except Exception:  # pylint: disable=broad-except
                    self._errors.append("XML parsing failed: document "
                                        "information could not be gathered.")
                else:
                    yield md_model
