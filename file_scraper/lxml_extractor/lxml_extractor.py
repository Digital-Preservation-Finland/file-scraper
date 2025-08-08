"""Class for XML and HTML5 header encoding check with lxml. """

try:
    from lxml import etree
except ImportError:
    pass

from file_scraper.base import BaseExtractor
from file_scraper.logger import LOGGER
from file_scraper.lxml_extractor.lxml_model import LxmlMeta
from file_scraper.utils import normalize_charset


class LxmlExtractor(BaseExtractor):
    """Scrape character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported_metadata = [LxmlMeta]
    _only_wellformed = True  # Only well-formed check

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """
        This scraper is supported only if well-formedness is True. This
        scraper supports text/xml files regardless of version. Also
        text/html versions 4.01 and 5 are supported.

        BaseExtractor's is_supported is not intricate enough to handle such
        functionality, so it has to be overridden.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the extractor
        :returns: True if extractor is supported
        """
        if params is None:
            params = {}
        if mimetype == "text/xml" and check_wellformed:
            return True
        return super().is_supported(mimetype, version,
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
                self._errors.append(str(exception))
                return
            except OSError as exception:
                self._errors.append("Failed: missing file.")
                self._errors.append(str(exception))
                return

        self.streams = list(self.iterate_models(tree=tree))

        # Only log success message if at least one metadata model was added to
        # streams. Check that it corresponds to given charset.
        if self.streams:
            self._messages.append("Encoding metadata found.")
            if not self._params.get("charset", None):
                self._errors.append("Character encoding not defined.")
                return

            provided_encoding = self._params["charset"].upper()
            encoding = self.streams[0].charset()
            if encoding:
                encoding = encoding.upper()
            norm_encoding = normalize_charset(encoding)

            # If encoding was provided in the XML header, ensure
            # that it matches the encoding provided to the extractor beforehand
            # in either the original or normalized form
            encoding_matches = (
                    encoding is None
                    or provided_encoding in (encoding, norm_encoding)
            )
            if not encoding_matches:
                self._errors.append(
                    f"Found encoding declaration {encoding} from the file "
                    f"{self.filename}, but {self._params['charset']} was "
                    f"expected.")

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
                        LOGGER.debug(
                            "Testing that method '%s' returns a valid "
                            "value...",
                            method.__name__
                        )
                        method()
                except Exception:  # pylint: disable=broad-except
                    LOGGER.info(
                        "Field did not return a valid value", exc_info=True
                    )
                    self._errors.append("XML parsing failed: document "
                                        "information could not be gathered.")
                else:
                    yield md_model

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        # Version consists of 4 values. Expect the first 3 to follow SemVers
        major, minor, patch, extra = etree.LXML_VERSION
        libmajor, libminor, libpatch = etree.LIBXML_VERSION
        return {
            "lxml": {"version": f"{major}.{minor}.{patch}.{extra}"},
            "libxml2": {"version": f"{libmajor}.{libminor}.{libpatch}"}
        }
