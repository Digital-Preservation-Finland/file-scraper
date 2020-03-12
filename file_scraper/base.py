"""Base module for scrapers."""
from __future__ import unicode_literals

import abc
from file_scraper.utils import metadata, is_metadata


class BaseScraper(object):
    """Base scraper implements common methods for all scrapers."""
    # pylint: disable=too-many-instance-attributes

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
        self.streams = []
        self.filename = filename
        self._predefined_mimetype = mimetype
        self._predefined_version = version
        self._messages = []
        self._errors = []
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
        return any([x.is_supported(mimetype, version) for x in
                    cls._supported_metadata])

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

        if mimetype == "(:unav)" and allow_unav_mime:
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
                if ((allow_unav_version and version == "(:unav)") or
                        (allow_unap_version and version == "(:unap)")):
                    return

        # No supporting metadata models found.
        self._errors.append("MIME type %s with version %s is not supported." %
                            (mimetype, version))

    def iterate_models(self, **kwargs):
        """
        Iterate Scraper models and create streams.

        :kwargs: Model specific parameters
        """
        for md_class in self._supported_metadata:
            if md_class.is_supported(self._predefined_mimetype,
                                     self._predefined_version, self._params):
                self.streams.append(md_class(**kwargs))

    def errors(self):
        """
        Return the logged errors in a list.

        :returns: copied list containing the logged errors
        """
        return self._errors[:]

    def messages(self):
        """
        Return logged non-empty messages in a list.

        :returns: list containing the logged messages
        """
        return [message for message in self._messages if message]

    def info(self):
        """
        Return a dict containing class name, messages and errors.

        The returned dict contains keys "class", "messages" and "errors", each
        having a single string as a value.

        :returns: Info dict
        """
        return {"class": self.__class__.__name__,
                "messages": self.messages(),
                "errors": self.errors()}


class BaseMeta(object):
    """
    All metadata is formalized in common data model.

    BaseMeta class will define common metadata for all file formats, such as:
    filename, mimetype, version, checksum.

    Additional metadata and processing is implemented in subclasses.

    The error messages given by the scraper usually affects to some of the
    metadata fields of the model. For example, we should return "(:unav)"
    as mimetype (and version), if the file contains errors. In such case,
    some other scraper may be a better resolver for this.

    First example, if the validator supports only one particular file
    format, then the scraper can result the mimetype as a string, if there
    are no errors. Then it means that the file is compliant with the only
    supported (and originally predefined) format. If there are errors, then
    the validator does not really know the mimetype, and therefore "(:unav)"
    should be returned.

    Second example, if we give a PNG file predefined as GIF file, then
    a GIF scraper produces errors and PNG+GIF scraper does not. The GIF
    scraper can not give the mimetype, since it gives errors, and
    therefore it does not know what the file is. The PNG+GIF scraper
    can give the mimetype ONLY if it is able to resolve the mimetype and
    errors are not found.

    Third example, if we give an XML file as a Plain text file, then
    Plain text scrapers are run. These should result either text/plain
    as mimetype, or "(:unav)" if they are not sure about it. For Plain
    text files this is actually possible only if the scraper is a plain
    text specific scraper and no errors are found.

    If all the scrapers result "(:unav)" as mimetype, then the actual file
    format is unknown. There must be at least one scraper which resolves
    the mimetype and version.

    If the predefined mimetype differs from the resulted one, then it is
    the main scraper's responsibility to resolve this with an extra error
    message.
    """
    # pylint: disable=no-self-use

    _supported = {}
    _allow_versions = False

    @metadata()
    def mimetype(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return "(:unav)"

    @metadata()
    def version(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.
        Resolve only if unambiguous.

        :returns: "(:unav)"
        """
        return "(:unav)"

    @metadata()
    def index(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: 0
        """
        return 0

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


class BaseDetector(object):
    """Class to identify file format."""
    # pylint: disable=too-few-public-methods

    __metaclass__ = abc.ABCMeta

    def __init__(self, filename, mimetype=None, version=None):
        """
        Initialize detector.

        :filename: Path to the identified file
        :mimetype: The MIME type of the file from another source, e.g. METS.
        :version: Version of the file from another source, e.g. METS.
        """
        self.filename = filename  # File path
        self.mimetype = None  # Identified mimetype
        self.version = None  # Identified file version
        self.info = None  # Class name, messages, errors

        # Detectors can use the user-supplied MIME types and versions to refine
        # or even fully determine the file format.
        self._given_mimetype = mimetype
        self._given_version = version

    @abc.abstractmethod
    def detect(self):
        """Detect file. Must be implemented in detectors."""
        pass

    def get_important(self):
        # pylint: disable=no-self-use
        """
        Return dict of important values determined by the detector.

        By default this is an empty dict, but subclasses can override this
        method to add "mimetype" and/or "version" keys to the dict.
        """
        return {}
