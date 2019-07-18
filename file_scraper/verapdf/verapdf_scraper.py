"""PDF/A scraper."""
from __future__ import unicode_literals

try:
    import lxml.etree as ET
except ImportError:
    pass

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.verapdf.verapdf_model import VerapdfMeta
from file_scraper.utils import ensure_text, encode_path

VERAPDF_PATH = "/usr/share/java/verapdf/verapdf"


class VerapdfScraper(BaseScraper):
    """PDF/A scraper."""

    # Supported mimetypes and versions
    _supported_metadata = [VerapdfMeta]
    _only_wellformed = True  # Only well-formed check

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

        shell = ProcessRunner(cmd)
        if shell.returncode != 0:
            raise VeraPDFError(ensure_text(shell.stderr))
        self._messages.append(ensure_text(shell.stdout))

        try:
            report = ET.fromstring(shell.stdout)
            if report.xpath("//batchSummary")[0].get("failedToParse") == "0":
                compliant = report.xpath(
                    "//validationReport")[0].get("isCompliant")
                if compliant == "false":
                    self._errors.append(ensure_text(shell.stdout))
                profile = \
                    report.xpath("//validationReport")[0].get("profileName")
            else:
                self._errors.append(ensure_text(shell.stdout))
        except ET.XMLSyntaxError:
            self._errors.append(ensure_text(shell.stderr))

        if self.well_formed:
            for md_class in self._supported_metadata:
                self.streams.append(md_class(profile, self._given_mimetype,
                                             self._given_version))
                self._check_supported()


class VeraPDFError(Exception):
    """
    VeraPDF Error.

    Raised if VeraPDF does not run successfully.
    """

    pass
