"""PDF/A scraper."""

try:
    import lxml.etree as ET
except ImportError:
    pass

from file_scraper.base import BaseScraper, Shell
from file_scraper.utils import metadata

VERAPDF_PATH = '/usr/share/java/verapdf/verapdf'


class VeraPdf(BaseScraper):
    """PDF/A scraper."""

    # Supported mimetypes and versions
    _supported = {
        "application/pdf": ['A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a',
                            'A-3b', 'A-3u']}
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """
        Scrape file.

        :raises: VeraPDFError
        """
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        cmd = [VERAPDF_PATH, self.filename]

        shell = Shell(cmd)
        if shell.returncode != 0:
            raise VeraPDFError(shell.stderr)
        self.messages(shell.stdout)

        try:
            report = ET.fromstring(shell.stdout)
            if report.xpath('//batchSummary')[0].get('failedToParse') == '0':
                compliant = report.xpath(
                    '//validationReport')[0].get('isCompliant')
                if compliant == 'false':
                    self.errors(shell.stdout)
                profile = \
                    report.xpath('//validationReport')[0].get('profileName')
                self.version = 'A' + profile.split("PDF/A")[1].split(
                    " validation profile")[0].lower()
            else:
                self.errors(shell.stdout)
        except ET.XMLSyntaxError:
            self.errors(shell.stderr)
        finally:
            self._check_supported()
            self._collect_elements()

    @metadata(important=True)
    def _version(self):
        """
        If the file is well-formed, return version, otherwise return None.

        For files that are not PDF/A, other scrapers need to be used to
        determine the version.
        """
        if self.well_formed:
            return self.version
        return None

    @metadata()
    def get_important(self):
        """Return important values."""
        if not self.well_formed:
            return {}
        important = {}
        important['version'] = self.version
        return important


    @metadata()
    def _stream_type(self):
        """Return file type."""
        return 'binary'

    def importants(self):
        """Important metadata that should have priority when combining metadata.
        Additional logic added that the important data has to be well_formed.
        :return: Dictionary of metadata and their values.
        """
        if not self.well_formed:
            return {}
        return self._importants


class VeraPDFError(Exception):
    """
    VeraPDF Error.

    Raised if VeraPDF does not run successfully.
    """

    pass
