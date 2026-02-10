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
        # Try to parse file without 'recover' option first. This ensures
        # that SyntaxError is raised for example when unsupported
        # encoding is used in XML header
        tree = None
        parser = etree.XMLParser(
            dtd_validation=False,
            no_network=True,
            resolve_entities=False,
            recover=False,
        )
        with self.filename.open("rb") as file_:
            try:
                tree = etree.parse(file_, parser)
            except OSError:
                # OSError could be caused for example by invalid
                # bytes in character encoding, in which case parsing the
                # file with 'recover' option could work.
                pass
            except etree.XMLSyntaxError as exception:
                # Parsing without 'recover' option might raise
                # XMLSyntaxErrors at least for some valid HTML files, so
                # we have to parse with 'recover' option.
                if exception.code == 32:
                    # libxml2 error XML_ERR_UNSUPPORTED_ENCODING
                    # This error would be omitted, if 'recover' option
                    # would be used.
                    self._errors.append(str(exception))
                    return

        # If parsing without 'recover' option fails, try to parse with
        # 'recover' option.
        if not tree:
            parser = etree.XMLParser(
                dtd_validation=False,
                no_network=True,
                resolve_entities=False,
                recover=True,
            )
            with self.filename.open("rb") as file_:
                try:
                    tree = etree.parse(file_, parser)
                except etree.XMLSyntaxError as exception:
                    self._errors.append("Failed: document is not well-formed.")
                    self._errors.append(str(exception))
                    return

        self.streams = list(self.iterate_models(tree=tree))
        if not self.streams:
            # Because the default implementation of is_supported method
            # is overwritten in this extractor class, this extractor
            # supports file formats that are not supported by any
            # metadata model (for example text/xml version foo).
            # For those file formats, the extractor does not produce any
            # streams, which leads to error, i.e. the files are always
            # not well-formed.
            return

        self._messages.append("Encoding metadata found.")
        if not self._predefined_charset:
            self._errors.append("Character encoding not defined.")
            return

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
