"""Base module for scrapers."""
import abc
import subprocess
from file_scraper.utils import run_command, ensure_str, metadata


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
        self._only_wellformed = False
        self._check_wellformed = check_wellformed
        self._params = params if params is not None else {}

    def iter_streams(self):
        """Iterate through all streams."""
        for stream in self.streams:
            yield stream

    @property
    def well_formed(self):
        """
        Return well-formedness status of the scraped file.

        :returns: None if scraper does not check well-formedness, True if the
                  file has been scraped without errors and otherwise False
        """
        # toimii nyt kuten vanhassa paitsi ettei None ole mahdollisuus
        if not self._check_wellformed:
            return None
        return len(self._messages) > 0 and len(self._errors) == 0

        # poc-toteutus:
        # """Return True if all streams are well-formed, otherwise False."""
        # return all([x.well_formed() for x in self.iter_streams()])

    @classmethod
    def is_supported(cls, mimetype, version=None, check_wellformed=True):
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
        :returns: True if the MIME type and version are supported, False if not
        """
        if cls._only_wellformed and not check_wellformed:
            return False
        return any([x.is_supported(mimetype, version) for x in
                    cls._supported_metadata])

    def _check_supported(self):
        """
        Check that the determined MIME type and version are supported.

        :raises: UnsupportedTypeException if the MIME type and version are not
                 supported
        """
        mimetype = self.streams[0].mimetype()
        version = self.streams[0].version()

        if mimetype is None:
            raise UnsupportedTypeException("None is not a supported MIME "
                                           "type.")
        elif not self.is_supported(mimetype, version):
            raise UnsupportedTypeException("MIME type %s with version %s is "
                                           "not supported." % (mimetype,
                                                               version))

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

    _supported = []
    _allow_versions = False

    @metadata()
    def mimetype(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

        :returns: "(:unav)"
        """
        return "(:unav)"

    @metadata()
    def version(self):
        """
        BaseMeta does no real scraping. Should be implemented in subclasses.

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

    def to_dict(self):
        """
        Construct a dict containing all metadata obtainable by this model.

        All streams are kept as-is, container metadata is not separated to the
        first stream.

        :returns: Dict containing the scraped metadata
        """
        stream = {}
        for methodname in dir(self):
            if not is_metadata(getattr(self, methodname)):
                continue
            stream[methodname] = getattr(self, methodname)()
        return stream

    @classmethod
    def is_supported(cls, mimetype, version=None):
        """
        Report whether this model supports the given MIME type and version.

        Version None is considered to be a supported version.

        :mimetype: MIME type to be checked
        :version: Version to be checked, defaults to None
        :returns: True if MIME type is supported and all versions are allowed
                  or the version is supported too.
        """
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


class Shell(object):
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


class UnsupportedTypeException(Exception):
    """Exception for when scraper is used with unsupported MIME type/version"""
    pass


class SkipElementException(Exception):
    """Exception to tell the iterator to skip the element.
    We are not able to use None or '' since those are reserved for
    other purposes already.
    """


class ImportantMetadataAlreadyDefined(Exception):
    """Exception to tell that the given key has already been defined as
    important."""


class BaseDetector(object):
    """Class to identify file format."""
    # pylint: disable=too-few-public-methods

    __metaclass__ = abc.ABCMeta

    def __init__(self, filename):
        """Initialize detector."""
        self.filename = filename  # File path
        self.mimetype = None  # Identified mimetype
        self.version = None  # Identified file version
        self.info = None  # Class name, messages, errors

    @abc.abstractmethod
    def detect(self):
        """Detect file. Must be implemented in detectors."""
        pass


def concat(lines, prefix=""):
    """
    Join given list of strings to single string separated with newlines.

    :lines: List of string to join
    :prefix: Prefix to prepend each line with
    :returns: Joined lines as string
    """
    return "\n".join(["%s%s" % (prefix, line) for line in lines])
