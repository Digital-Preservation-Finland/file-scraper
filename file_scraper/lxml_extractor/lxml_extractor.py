"""Class for XML and HTML5 header encoding check with lxml."""

from lxml import etree

from file_scraper.base import BaseExtractor
from file_scraper.defaults import COMPATIBLE_ENCODINGS
from file_scraper.lxml_extractor.lxml_model import LxmlMeta


class LxmlExtractor(BaseExtractor[LxmlMeta]):
    """Scrape character encoding from XML/HTML header."""

    # We use JHOVE for HTML4 and XHTML files.
    _supported_metadata = [LxmlMeta]
    _only_wellformed = True  # Only well-formed check
    _allow_unav_mime = True
    _allow_unav_version = True

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

    def _extract(self):
        """Scrape file."""
        parser = etree.XMLParser(dtd_validation=False, no_network=True,
                                 recover=True, resolve_entities=False)
        with open(self.filename, "rb") as file_:
            try:
                tree = etree.parse(file_, parser)
            except etree.XMLSyntaxError as exception:
                self._errors.append("Failed: document is not well-formed.")
                self._errors.append(str(exception))
                return

        self.streams = list(self.iterate_models(tree=tree))

        # Only log success message if at least one metadata model was added to
        # streams. Check that it corresponds to given charset.
        if self.streams:
            self._messages.append("Encoding metadata found.")
            if not self._predefined_charset:
                self._errors.append("Character encoding not defined.")
                return

            # Note that if header does not contain encoding, lxml will
            # assume it is UTF-8!
            encoding_from_header = self.streams[0].charset()

            # If encoding was provided in the XML header, ensure
            # that it is compatible with the detected/predefined
            # encoding
            if encoding_from_header != self._predefined_charset \
                    and encoding_from_header \
                    not in COMPATIBLE_ENCODINGS[self._predefined_charset]:
                self._errors.append(
                    f"Found encoding declaration {encoding_from_header} from "
                    f"the file {self.filename}, which is not compatible with "
                    f"{self._predefined_charset}"
                )

    def tools(self):
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        # Version consists of 4 values. Expect the first 3 to follow SemVers
        major, minor, patch, extra = etree.LXML_VERSION
        libmajor, libminor, libpatch = etree.LIBXML_VERSION
        return {
            "lxml": {"version": f"{major}.{minor}.{patch}.{extra}"},
            "libxml2": {"version": f"{libmajor}.{libminor}.{libpatch}"}
        }
