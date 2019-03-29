"""Module for checking files with Jhove scraper."""
import os
import abc

try:
    import lxml.etree
except ImportError:
    pass

from file_scraper.base import BaseScraper, Shell
from file_scraper.utils import metadata, ensure_str

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove',
              'aes': 'http://www.aes.org/audioObject'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, 'bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/jhove-apps-1.18.1.jar') + ':' + EXTRA_JARS


class JHove(BaseScraper):
    """Base class for Jhove file format scraper."""

    __metaclass__ = abc.ABCMeta
    _jhove_module = None  # JHove module

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize JHove base scarper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._report = None  # JHove report
        self._shell = None  # Shell object
        super(JHove, self).__init__(filename, mimetype, check_wellformed,
                                    params)

    def scrape_file(self):
        """
        Run JHove command and store XML output to self.report.
        """
        exec_cmd = ['jhove', '-h', 'XML', '-m',
                    self._jhove_module, self.filename]
        self._shell = Shell(exec_cmd)

        if self._shell.returncode != 0:
            self.errors("JHove returned error: %s\n%s" % (
                self._shell.returncode, self._shell.stderr))

        self._report = lxml.etree.fromstring(self._shell.stdout)

        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return

        status = self.report_field("status")
        self.messages(status)
        if 'Well-Formed and valid' not in status:
            self.errors("Validator returned error: %s\n%s" % (
                ensure_str(self._shell.stdout),
                ensure_str(self._shell.stderr)
            ))
        self._check_supported()
        self._collect_elements()

    @metadata()
    def _s_mimetype(self):
        """Return mimetype given by JHove."""
        return self.report_field('mimeType')

    @metadata()
    def _s_version(self):
        """Return version given by JHove."""
        return self.report_field("version")

    @abc.abstractmethod
    @metadata()
    def _s_stream_type(self):
        """Implement in the file format specific classes."""
        pass

    def report_field(self, field):
        """Return field value from JHoves XML output stored to self.report."""
        if self._report is None:
            return None
        query = '//j:%s/text()' % field
        results = self._report.xpath(query, namespaces=NAMESPACES)
        if not results:
            return None
        return '\n'.join(results)
