"""
This is an PDF/A scraper.
"""
try:
    import lxml.etree as ET
except ImportError:
    pass

from dpres_scraper.base import BaseScraper, Shell


VERAPDF_PATH = '/usr/share/java/verapdf/verapdf'


class VeraPdf(BaseScraper):
    """
    PDF/A scraper
    """
    _supported = {
        "application/pdf": ['A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a',
                            'A-3b', 'A-3u']}
    _only_wellformed = True

    def scrape_file(self):
        """Scrape file
        """
        if self.version is not None:
            flavour = self.version[-2:]
            cmd = [VERAPDF_PATH, '-f', flavour, self.filename]
        else:
            cmd = [VERAPDF_PATH, self.filename]

        shell = Shell(cmd)
        if shell.returncode != 0:
            raise VeraPDFError(shell.stderr)
        self.messages(shell.stdout)

        try:
            report = ET.fromstring(shell.stdout)
            if report.xpath('//batchSummary')[0].get('failedToParse') == '0':
                valid = report.xpath(
                    '//validationReport')[0].get('isCompliant')
                if valid == 'false':
                    self.errors(shell.stdout)
            else:
                self.errors(shell.stdout)
        except ET.XMLSyntaxError:
            self.errors(shell.stderr)
        finally:
            self._collect_elements()

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class VeraPDFError(Exception):
    """
    VeraPDF Error
    """
    pass
