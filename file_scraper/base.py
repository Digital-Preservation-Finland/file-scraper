"""Base module for scrapers."""
from __future__ import unicode_literals

import abc
import subprocess
from file_scraper.utils import run_command, metadata, is_metadata, concat


class BaseScraper(object):
    """Base scraper implements common methods for all scrapers."""

    _supported_metadata = []
    _only_wellformed = False

    def __init__(self, filename, check_wellformed=True, params=None):
        """
        Initialize scraper.

        BaseScraper.stream will contain all streams in standardized metadata
        data model.

        :filename: Path to the file that is to be scraped
        :check_wellformed: True for full scraping, False for skipping the well-
                           formedness check
        :params: Extra parameters that some scrapers can use.
        """
        self.streams = []
        self.filename = filename
        self._messages = []
        self._errors = []
        self._check_wellformed = check_wellformed
        self._params = params if params is not None else {}

        self._given_mimetype = self._params.get("mimetype", None)
        self._given_version = self._params.get("version", None)
        if self._given_mimetype:
            if self._given_version:
                self._messages.append("MIME type and version not scraped, "
                                      "using user-supplied values.")
            else:
                self._messages.append("MIME type not scraped, using user-"
                                      "supplied value.")

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.

        :returns: None if scraper does not check well-formedness, True if the
                  file has been scraped without errors and otherwise False
        """
        if not self._check_wellformed:
            return None
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

    def errors(self):
        """
        Return the logged errors.

        Each error is on its own line, preceded py "ERROR: ".

        :returns: string containing the logged errors
        """
        return concat(self._errors, "ERROR: ")

    def messages(self):
        """
        Return logged messages as a single string, one message per line.

        :returns: string containing the logged messages
        """
        return concat(self._messages)

    def info(self):
        """
        Return a dict containing class name, messages and errors.

        The returned dict contains keys "class", "messages" and "errors", each
        having a single string as a value.
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
    """
    # pylint: disable=no-self-use

    _supported = {}
    _allow_versions = False

    def __init__(self, mimetype=None, version=None):
        """
        Initialize the metadata model.

        Metadata models can be given a mimetype and/or version obtained from
        another source such as METS. Metadata models must be implemented so
        that if supplied, these values are used instead of values determined
        based on the file.
        """
        self._given_mimetype = mimetype
        self._given_version = version

    @metadata()
    def mimetype(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: "(:unav)"
        """
        if self._given_mimetype:
            return self._given_mimetype
        return "(:unav)"

    @metadata()
    def version(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: "(:unav)"
        """
        if self._given_mimetype and self._given_version:
            return self._given_version
        return "(:unav)"

    @metadata()
    def index(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: 0
        """
        return 0

    # pylint: disable=unused-argument
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
        if mimetype not in cls._supported:
            return False
        if version in cls._supported[mimetype] + [None] or cls._allow_versions:
            return True
        return False
    # pylint: enable=unused-argument

    def iterate_metadata_methods(self):
        """Iterate through all metadata methods."""
        for method in dir(self):
            if is_metadata(getattr(self, method)):
                yield getattr(self, method)

    @classmethod
    def supported_mimetypes(cls):
        """Return the dict containing supported mimetypes and versions."""
        return cls._supported


class ProcessRunner(object):
    """Shell command handler for non-Python 3rd party software."""

    def __init__(self, command, output_file=subprocess.PIPE, env=None):
        """
        Initialize instance.

        :command: Command to execute as list
        :output_file: Output file handle
        :env: Environment variables
        """
        self.command = command

        self._stdout = None
        self._stderr = None
        self._returncode = None
        self.output_file = output_file
        self.env = env

    @property
    def returncode(self):
        """
        Returncode from the command.

        :returns: Returncode
        """
        return self.run()["returncode"]

    @property
    def stderr(self):
        """
        Standard error output from the command.

        :returns: Stderr as string
        """
        return self.run()["stderr"]

    @property
    def stdout(self):
        """
        Command standard error output.

        :returns: Stdout as string
        """
        return self.run()["stdout"]

    def run(self):
        """
        Run the command and store results to class attributes for caching.

        :returns: Returncode, stdout, stderr as dictionary
        """
        if self._returncode is None:
            (self._returncode, self._stdout,
             self._stderr) = run_command(cmd=self.command,
                                         stdout=self.output_file,
                                         env=self.env)
        return {
            "returncode": self._returncode,
            "stderr": self._stderr,
            "stdout": self._stdout
            }


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
