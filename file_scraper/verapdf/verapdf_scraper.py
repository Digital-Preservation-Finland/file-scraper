"""PDF/A scraper."""
from __future__ import unicode_literals

try:
    import lxml.etree as ET
except ImportError:
    pass

import distutils.spawn
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
        verapdf_loc = VERAPDF_PATH
        if distutils.spawn.find_executable("verapdf") is not None:
            verapdf_loc = "verapdf"
        # --nonpdfext flag allows also files without the .pdf extension
        cmd = [verapdf_loc, encode_path(self.filename), "--nonpdfext"]
        shell = Shell(cmd)

        # If --nonpdfext flag is not supported, it does not affect to
        # returncode
        if shell.returncode not in OK_CODES:
            self._errors.append("Return code: %s" % shell.returncode)
            self._errors.append(shell.stderr)
            self._check_supported()
            return

        # Filter error about --nonpdfext flag not being supported
        errors = filter_errors(shell.stderr)
        if errors:
            self._errors.append(errors)

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
            pass  # XML is empty. We already added all errors.

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, profile=profile))

        self._check_supported()


def filter_errors(stderr):
    """Filter errors for the case where --nonpdfext flag is not supported.

    :stderr: stderr from veraPDF
    :returns: Filtered errors
    """
    if stderr:
        error_list = []
        for err_line in stderr.splitlines(True):
            if "--nonpdfext doesn't exist." in err_line:
                header = "org.verapdf.apps.utils.ApplicationUtils "\
                    "filterPdfFiles"
                if error_list and header in error_list[-1]:
                    error_list.pop()  # Remove already added error header
            else:
                error_list.append(err_line)
        return "".join(error_list)
    else:
        return None
