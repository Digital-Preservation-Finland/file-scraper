"""PDF/A scraper."""
from __future__ import unicode_literals

try:
    import lxml.etree as ET
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.config import VERAPDF_PATH
from file_scraper.verapdf.verapdf_model import VerapdfMeta
from file_scraper.utils import encode_path


class VerapdfScraper(BaseScraper):
    """PDF/A scraper."""

    # Supported mimetypes and versions
    _supported_metadata = [VerapdfMeta]

    def scrape_file(self):
        """
        Scrape file.

        :raises: VeraPDFError
        """
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not "
                                  "used.")
            return
        cmd = [VERAPDF_PATH, encode_path(self.filename)]

        shell = Shell(cmd)
        if shell.returncode != 0:
            raise VeraPDFError(shell.stderr)
        self._messages.append(shell.stdout)
        profile = None

        try:
            report = ET.fromstring(shell.stdout_raw)
            if report.xpath("//batchSummary")[0].get("failedToParse") == "0":
                compliant = report.xpath(
                    "//validationReport")[0].get("isCompliant")
                if compliant == "false":
                    self._errors.append(shell.stdout)
                profile = \
                    report.xpath("//validationReport")[0].get("profileName")
            else:
                self._errors.append(shell.stdout)
        except ET.XMLSyntaxError:
            self._errors.append(shell.stderr)

        self.iterate_models(errors=self._errors, profile=profile)

        self._check_supported()


class VeraPDFError(Exception):
    """
    VeraPDF Error.

    Raised if VeraPDF does not run successfully.
    """
    pass
