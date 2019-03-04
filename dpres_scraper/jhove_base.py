"""Module for validating files with Jhove validator"""
import os
import abc
try:
    import lxml.etree
except ImportError:
    pass

from dpres_scraper.base import BaseScraper, Shell

NAMESPACES = {'j': 'http://hul.harvard.edu/ois/xml/ns/jhove',
              'aes': 'http://www.aes.org/audioObject'}
JHOVE_HOME = '/usr/share/java/jhove'
EXTRA_JARS = os.path.join(JHOVE_HOME, 'bin/JhoveView.jar')
CP = os.path.join(JHOVE_HOME, 'bin/jhove-apps-1.18.1.jar') + ':' + EXTRA_JARS


class JHove(BaseScraper):
    """Base class for Jhove file format validator"""

    __metaclass__ = abc.ABCMeta
    _jhove_module = None

    def __init__(self, filename, mimetype, validation=True):
        """
        """
        self._report = None
        self._shell = None
        super(JHove, self).__init__(filename, mimetype, validation)

    def scrape_file(self):
        """Run JHove command and store XML output to self.report"""

        exec_cmd = ['jhove', '-h', 'XML', '-m',
                    self._jhove_module, self.filename]
        self._shell = Shell(exec_cmd)

        if self._shell.returncode != 0:
            self.errors("JHove returned error: %s\n%s" % (
                self._shell.returncode, self._shell.stderr))

        self._report = lxml.etree.fromstring(self._shell.stdout)
        status = self.report_field("status")
        self.messages(status)
        if 'Well-Formed and valid' not in status:
            self.errors("Validator returned error: %s\n%s" % (
                self._shell.stdout, self._shell.stderr))
        self._collect_elements()

    def _s_mimetype(self):
        """Return mimetype given by JHove
        """
        return self.report_field('mimeType')

    def _s_version(self):
        """Return version given by JHove
        """
        return self.report_field("version")

    def _s_stream_type(self):
        """Return stream type
        """
        return None

    def report_field(self, field):
        """Return field value from JHoves XML output stored to self.report."""
        query = '//j:%s/text()' % field
        results = self._report.xpath(query, namespaces=NAMESPACES)
        return '\n'.join(results)
