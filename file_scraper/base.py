"""Base module for scrapers."""
import abc
import subprocess
from file_scraper.utils import (run_command, combine_metadata, ensure_str,
                                metadata, is_metadata, is_important)


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
            'returncode': self._returncode,
            'stderr': self._stderr,
            'stdout': self._stdout
        }


class BaseScraper(object):
    """Base class for scrapers."""
    # pylint: disable=too-many-instance-attributes

    __metaclass__ = abc.ABCMeta

    _supported = {}  # Dictionary of supported mimetypes and versions
    _allow_versions = False  # True: Allow other detected versions
    _only_wellformed = False  # True if the scraper does just well-formed

    # check, False otherwise  # noqa:E116,E114

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                            identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        if params is None:
            params = {}
        self.filename = filename  # File name
        self.mimetype = mimetype  # Resulted mime type
        self._version = None  # Resulted file format version
        self.streams = {}  # Resulted streams
        self.info = None  # Class name, messages, errors
        self._importants = {}  # Important metadata and their values
        self._messages = []  # Diagnostic messages in scraping
        self._errors = []  # Errors in scraping
        self._check_wellformed = check_wellformed  # True for well-formed check
        self._params = params  # Extra parameters needed

    @classmethod
    def is_supported(cls, mimetype, version=None,
                     check_wellformed=True, params=None):
        """
        Return true if given MIME type and version are supported.

        Check
        (1) if mimetype is supported,
        (2) if version matches (if needed),
        (3) if well-formed check is needed.

        :mimetype: Identified mimetype
        :version: Identified version (if needed)
        :check_wellformed: True for the full well-formed check, False for just
                            identification and metadata scraping
        :params: Extra parameters needed for the scraper.
                 Used in some scrapers which override this method.
        :returns: True if scraper is supported
        """
        # pylint: disable=unused-argument
        if mimetype in cls._supported and \
                (version in cls._supported[mimetype] + [None] or
                 cls._allow_versions) and \
                (check_wellformed or not cls._only_wellformed):
            return True
        return False

    @abc.abstractmethod
    def scrape_file(self):
        """
        Must implement the actual scraping in the scrapers.

        self._check_supported() is recommended after scraping.
        self._collect_elements() must be called in the end.
        """
        pass

    def messages(self, message=None):
        """
        Return diagnostic messages.

        :message: New message to add to the messages
        """
        if message is not None:
            self._messages.append(ensure_str(message))
        return concat(self._messages)

    def errors(self, error=None):
        """
        Return error messages.

        :error: New error to add to the errors
        """
        err_msg = ensure_str(error) if error is not None else None
        if err_msg is not None and err_msg != "":
            self._errors.append(err_msg)
        return concat(self._errors, 'ERROR: ')

    @property
    def well_formed(self):
        """Check if file is well-formed."""
        if not self._check_wellformed:
            return None
        return len(self._messages) > 0 and len(self._errors) == 0

    def _collect_elements(self):
        """
        Collect metadata for the elements in streams.

        Values returned from methods '_s_*' will be collected.
        """
        for _ in self.iter_tool_streams(None):
            metadata = {}
            for method in dir(self):
                if is_metadata(getattr(self, method)):
                    try:
                        metadata[method[3:]] = getattr(self, method)()
                    except SkipElementException:
                        # happens when <method>-method is not to be indexed.
                        pass
                if is_important(getattr(self, method)):
                    self._add_important(method[3:], getattr(self, method)())
            dict_meta = {metadata['index']: metadata}
            self.streams = combine_metadata(self.streams, dict_meta)
        self.mimetype = self.streams[0]['mimetype']
        self._version = self.streams[0]['version']
        self.info = {'class': self.__class__.__name__,
                     'messages': self.messages(),
                     'errors': self.errors()}

    def _check_supported(self):
        """Check that resulted mimetype and possible version are supported."""
        if self._s_mimetype() is None:
            self.errors("None is not supported mimetype.")
        elif self._s_mimetype() and self._s_mimetype() not in self._supported:
            self.errors("Mimetype %s is not supported." % self._s_mimetype())
        elif self._s_version() and self._s_version() not in \
                self._supported[self._s_mimetype()]:
            self.errors("Version %s is not supported." % self._s_version())

    # pylint: disable=no-self-use,unused-argument
    def iter_tool_streams(self, stream_type):
        """
        Iterate streams with given stream type.

        Implement in scraper, if needed. Otherwise yield empty dict.
        """
        yield {}

    def set_tool_stream(self, index):
        """
        Set stream.

        Implement in scraper, if needed. Otherwise allow call but do nothing.
        """
        pass

    # Methods starting with '_s_' will be collected to the stream results.
    # All _s_ methods must return str, except _s_index, which returns int.
    # See: _collect_elements

    @metadata()
    def _s_mimetype(self):
        """Return mimetype."""
        return self.mimetype

    @metadata()
    def _s_version(self):
        """Return version."""
        return self.version()

    @metadata()
    def _s_index(self):
        """Return stream index."""
        return 0

    @abc.abstractmethod
    @metadata()
    def _s_stream_type(self):
        """Return stream type. Must be implemented in the scrapers."""
        pass

    def version(self):
        """Version of the file
        :return: Str if version assigned, else None.
        """
        return ensure_str(self._version) if self._version is not None else None

    def importants(self):
        """Important metadata that should have priority when combining metadata.
        :return: Dictionary of metadata and their values.
        """
        return self._importants

    def _add_important(self, key, value):
        """Key along with the value added as important metadata.
        Exception is raised if the key has already been defined important.
        :param key: Metadata index key.
        :param value: Metadata value.
        :raises: ImportantMetadataAlreadyDefined
        """
        if key in self._importants and self._importants[key] != value:
            raise ImportantMetadataAlreadyDefined(
                '[%s] index is already important with [%s]. '
                'Incoming value: [%s]' % (key, self._importants[key], value))
        self._importants[key] = value


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
