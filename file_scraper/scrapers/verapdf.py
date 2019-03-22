"""PDF/A scraper.
"""
try:
    import lxml.etree as ET
except ImportError:
    pass

from file_scraper.base import BaseScraper, Shell


VERAPDF_PATH = '/usr/share/java/verapdf/verapdf'


class VeraPdf(BaseScraper):
    """
    PDF/A scraper
    """
    # Supported mimetypes and versions
    _supported = {
        "application/pdf": ['A-1a', 'A-1b', 'A-2a', 'A-2b', 'A-2u', 'A-3a',
                            'A-3b', 'A-3u']}
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """Scrape file
        """
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

    def _s_version(self):
        """We let other scrapers decide version, if not well-formed.
        """
        if self.well_formed:
            return self.version
        return None

    def is_important(self):
        """Return important values
        """
        if not self.well_formed:
            return {}
        important = {}
        important['version'] = self.version
        return important

    def _s_stream_type(self):
        """Return file type
        """
        return 'binary'


class VeraPDFError(Exception):
    """
    VeraPDF Error
    """
    pass
