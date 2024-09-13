"""Base module for scrapers."""

import abc

from file_scraper.defaults import UNAP, UNAV
from file_scraper.utils import (metadata, is_metadata, encode_path,
                                filter_unwanted_chars)

# Object inheritance is needed as long as we support Python 2 to explicitly use
# new-style classes.
# pylint: disable=useless-object-inheritance


class _BaseScraperDetector:
    """Base class for Scrapers and detectors."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, filename, mimetype=None, version=None):
        """Initialize scraper/detector.

        :filename: Path to the file that is to be scraped
        """
        # The filename passed here should already be encoded, but it is
        # encoded also here to simplify testing Scrapers.
        if filename is not None:
            filename = encode_path(filename)
        self.filename = filename
        self._predefined_mimetype = mimetype
        self._predefined_version = version
        self._messages = []
        self._errors = []
        self._tools = []

    def errors(self):
        """Return the logged errors in a list.

        :returns: copied list containing the logged errors
        """
        return [filter_unwanted_chars(error) for
                error in self._errors if error]

    def messages(self):
        """Return logged non-empty messages in a list.

        :returns: list containing the logged messages
        """
        return [filter_unwanted_chars(message) for
                message in self._messages if message]

    def tools(self):
        """Return used software tools in a list.

        :returns: list containing the tools used
        """
        return [tool for tool in self._tools if tool]

    def info(self):
        """Return basic info of detector/scraper.

        The returned dict contains keys "class", "messages", "errors"
        and "tools", where:
            class: Name of the class
            messages: List of info messages
            errors: List of errors
            tools: List of tools used

        :returns: Info dict
        """
        return {"class": self.__class__.__name__,
                "messages": self.messages(),
                "errors": self.errors(),
                "tools": self.tools()}


class BaseScraper(_BaseScraperDetector):
    """Base scraper implements common methods for all scrapers."""

    _supported_metadata = []
    _only_wellformed = False

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize scraper.

        BaseScraper.stream will contain all streams in standardized metadata
        data model.

        :filename: Path to the file that is to be scraped
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters that some scrapers can use.
        """
        super().__init__(filename, mimetype, version)
        self.streams = []
        self._params = params if params is not None else {}

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.

        :returns: None if scraper does not check well-formedness, True if the
                  file has been scraped without errors and otherwise False
        """
        return len(self._messages) > 0 and len(self._errors) == 0

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True,
                     params=None):  # pylint: disable=unused-argument
        """
        Report whether the scraper supports the given MIME type and version.

        The scraper is considered to support the MIME type and version
        combination if at least one of the metadata models supported by the
        scraper supports the combination. If the scraper can only be used to
        check the well-formedness of the file and well-formedness check is not
        wanted, False is returned.

        :mimetype: MIME type of a file
        :version: Version of a file. Defaults to None.
        :check_wellformed: True for scraping with well-formedness check, False
                           for skipping the check. Defaults to True.
        :params: dict of other parameters that can be used by overriding
                 methods
        :returns: True if the MIME type and version are supported, False if not
        """
        if cls._only_wellformed and not check_wellformed:
            return False
        return any(x.is_supported(mimetype, version) for x in
                   cls._supported_metadata)

    def _check_supported(self, allow_unav_mime=False,
                         allow_unav_version=False,
                         allow_unap_version=False):
        """
        Check that the determined MIME type and version are supported.

        :allow_unav_mime: True if (:unav) is an acceptable MIME type
        :allow_unav_version: True if (:unav) is an acceptable version
        :allow_unap_version: True if (:unap) is an acceptable version
        """
        # If there are no streams, the scraper does not support the determined
        # MIME type and version combination at all (i.e. the initial MIME type
        # guess used to choose scrapers has been inaccurate).
        if not self.streams:
            self._errors.append("MIME type not supported by this scraper.")
            return

        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()

        if mimetype is None:
            self._errors.append("None is not a supported MIME type.")

        if mimetype == UNAV and allow_unav_mime:
            return

        for md_class in self._supported_metadata:
            if mimetype in md_class.supported_mimetypes():
                # version is in the list of supported versions
                if version in md_class.supported_mimetypes()[mimetype]:
                    return
                # all versions are supported
                if not md_class.supported_mimetypes()[mimetype]:
                    return
                # version is (:unav) or (:unap) but that is allowed
                if ((allow_unav_version and version == UNAV) or
                        (allow_unap_version and version == UNAP)):
                    return

        # No supporting metadata models found.
        self._errors.append(
            f"MIME type {mimetype} with version {version} is not supported."
        )

    def iterate_models(self, **kwargs):
        """
        Iterate Scraper models.

        :kwargs: Model specific parameters
        :returns: Metadata model
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(self._predefined_mimetype,
                                     self._predefined_version, self._params):
                yield md_class(**kwargs)


class BaseMeta:
    """
    All metadata is formalized in common data model.

    BaseMeta class will define common metadata for all file formats, such as:
    filename, mimetype, version, checksum.

    Additional metadata and processing is implemented in subclasses.
    """

    _supported = {}
    _allow_versions = False

    @metadata()
    def mimetype(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @metadata()
    def version(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @metadata()
    def index(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: 0
        """
        return 0

    @metadata()
    def stream_type(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return UNAV

    @classmethod
    def is_supported(cls, mimetype, version=None, params=None):
        """
        Report whether this model supports the given MIME type and version.

        Version None is considered to be a supported version.

        :mimetype: MIME type to be checked
        :version: Version to be checked, defaults to None
        :params: Parameter dict that can be used by some metadata models.
        :returns: True if MIME type is supported and all versions are allowed
                  or the version is supported too.
        """
        # pylint: disable=unused-argument
        if mimetype not in cls._supported:
            return False
        if version in cls._supported[mimetype] + [None] or cls._allow_versions:
            return True
        return False

    def iterate_metadata_methods(self):
        """Iterate through all metadata methods."""
        for method in dir(self):
            if is_metadata(getattr(self, method)):
                yield getattr(self, method)

    @classmethod
    def supported_mimetypes(cls):
        """Return the dict containing supported mimetypes and versions."""
        return cls._supported


class BaseDetector(_BaseScraperDetector):
    """Class to identify file format."""

    def __init__(self, filename, mimetype=None, version=None):
        """Initialize detector.

        Detectors can use the user-supplied MIME types and versions to
        refine or even fully determine the file format.

        :filename: Path to the identified file
        :mimetype: The MIME type of the file from another source, e.g. METS.
        :version: Version of the file from another source, e.g. METS.
        """
        super().__init__(filename, mimetype, version)

        self.mimetype = None  # Identified mimetype
        self.version = None  # Identified file version

    @property
    def well_formed(self):
        """Return well-formedness status of the detected file.

        This can be either None or False, because detectors do not validate.

        :returns: False if errors in detection, None otherwise.
        """
        return False if self._errors else None

    @abc.abstractmethod
    def detect(self):
        """Detect file. Must be implemented in detectors."""

    def get_important(self):
        """
        Return dict of important values determined by the detector.

        By default this is an empty dict, but subclasses can override this
        method to add "mimetype" and/or "version" keys to the dict.
        """
        return {}
