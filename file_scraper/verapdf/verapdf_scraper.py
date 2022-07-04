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

# Exit codes given by veraPDF that we don't want to immediately
# raise as fatal errors
# 0: All files parsed and valid PDF/A
# 1: All files parsed, some invalid PDF/A.
#    The files might still be valid PDFs, just not A format
# 7: Failed to parse one or more files.
#    The files are somehow broken/invalid PDFs
OK_CODES = [0, 1, 7]


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
        # --nonpdfext flag allows also files without the .pdf extension
        cmd = [VERAPDF_PATH, encode_path(self.filename), "--nonpdfext"]

        shell = Shell(cmd)
        if shell.returncode not in OK_CODES:
            raise VeraPDFError(shell.stderr)
        profile = None

        try:
            report = ET.fromstring(shell.stdout_raw)
            if report.xpath("//batchSummary")[0].get("failedToParse") == "0":
                compliant = report.xpath(
                    "//validationReport")[0].get("isCompliant")
                if compliant == "false":
                    self._errors.append(shell.stdout)
                else:
                    self._messages.append(shell.stdout)
                profile = \
                    report.xpath("//validationReport")[0].get("profileName")
            else:
                self._errors.append(shell.stdout)
        except ET.XMLSyntaxError:
            self._errors.append(shell.stderr)

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, profile=profile))

        self._check_supported()


class VeraPDFError(Exception):
    """
    VeraPDF Error.

    Raised if VeraPDF does not run successfully.
    """
