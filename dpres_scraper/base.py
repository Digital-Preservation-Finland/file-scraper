"""Base module for scrapers
"""
import abc
import subprocess
from dpres_scraper.utils import run_command
from dpres_scraper.utils import combine_metadata


class Shell(object):

    """Docstring for ShellTarget. """

    def __init__(self, command, output_file=subprocess.PIPE, env=None):
        """Initialize instance.

        :command: Command to execute as list
        """
        self.command = command

        self._stdout = None
        self._stderr = None
        self._returncode = None
        self.output_file = output_file
        self.env = env

    @property
    def returncode(self):
        """Returncode from the command

        :returns: Returncode

        """
        return self.run()["returncode"]

    @property
    def stderr(self):
        """Standard error output from the command

        :returns: Stdout as string

        """
        return self.run()["stderr"]

    @property
    def stdout(self):
        """Command standard error output.

        :returns: Stderr as string

        """
        return self.run()["stdout"]

    def run(self):
        """Run the command and store results to class attributes for caching.

        :returns: Returncode, stdout, stderr as dictionary

        """
        if self._returncode is None:
            (self._returncode, self._stdout,
             self._stderr) = run_command(
                cmd=self.command, stdout=self.output_file,
                env=self.env)

        return {
            'returncode': self._returncode,
            'stderr': self._stderr,
            'stdout': self._stdout
            }


class BaseScraper(object):
    """Base class for scrapers
    """

    __metaclass__ = abc.ABCMeta

    _supported = {}
    _only_wellformed = False

    def __init__(self, filename, mimetype, validation=True):
        """
        """
        self.filename = filename
        self.mimetype = mimetype
        self.version = None
        self.streams = {}
        self.info = None
        self._messages = []
        self._errors = []
        self._validation = validation

    def is_supported(self, version=None):
        """Return true if mimetype is supported, if version matches
        (if needed), and if validation is needed in scrapers which just
        validation.
        """
        if self.mimetype in self._supported and \
                (not self._supported[self.mimetype] or
                 version is None or
                 version in self._supported[self.mimetype]) and \
                (self._validation or not self._only_wellformed):
            return True
        return False

    @abc.abstractmethod
    def scrape_file(self):
        """Scrapers must implement scraping
        """
        pass

    def messages(self, message=None):
        """Return validation diagnostic messages"""
        if message is not None:
            self._messages.append(message)
        return concat(self._messages)

    def errors(self, error=None):
        """Return validation error messages"""
        if error is not None and error != "":
            self._errors.append(error)
        return concat(self._errors, 'ERROR: ')

    @property
    def well_formed(self):
        """Check if file is well-formed.
        """
        if not self._validation:
            return None
        return len(self._messages) > 0 and len(self._errors) == 0

    def _collect_elements(self):
        """Collect elements metadata
        """
        for _ in self.iter_tool_streams(None):
            metadata = {}
            for method in dir(self):
                if callable(getattr(self, method)) \
                        and method.startswith('_s_'):
                    item = getattr(self, method)()
                    if item != SkipElement:
                        metadata[method[3:]] = item
            dict_meta = {metadata['index']: metadata}
            self.streams = combine_metadata(self.streams, dict_meta)
        self.mimetype = self.streams[0]['mimetype']
        self.version = self.streams[0]['version']
        self.info = {'class': self.__class__.__name__,
                     'messages': self.messages(),
                     'errors': self.errors()}

    # pylint: disable=no-self-use,unused-argument
    def iter_tool_streams(self, stream_type):
        """Iterate streams with given stream type
        """
        yield {}

    def set_tool_stream(self, index):
        """Set stream. Implement in scraper, if needed.
        Otherwise allow call but do nothing.
        """
        pass

    def is_important(self):
        """Explain which values are more important
        """
        return {}

    def _s_mimetype(self):
        """Return mimetype
        """
        return self.mimetype

    def _s_version(self):
        """Return version
        """
        return self.version

    def _s_index(self):
        """Return stream index
        """
        return 0

    @abc.abstractmethod
    def _s_stream_type(self):
        """Return stream type
        """
        pass


class SkipElement:
    """Class used as a value to tell the iterator to skip the element.
    We are not able to use None or '' since those are reserved for
    other purposes already
    """
    pass


class BaseDetector(object):
    """Class to identify file format
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, filename):
        """Initialize detector
        """
        self.filename = filename
        self.mimetype = None
        self.version = None
        self.info = None

    @abc.abstractmethod
    def detect(self):
        """Detect file
        """
        pass


def concat(lines, prefix=""):
    """Join given list of strings to single string separated with newlines.

    :lines: List of string to join
    :prefix: Prefix to prepend each line with
    :returns: Joined lines as string

    """
    return "\n".join(["%s%s" % (prefix, line) for line in lines])
