"""PDF/A extractor."""

try:
    import lxml.etree as ET
except ImportError:
    pass

import re

from file_scraper.base import BaseExtractor
from file_scraper.logger import LOGGER
from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.verapdf.verapdf_model import VerapdfMeta

# Exit codes given by veraPDF that we don't want to immediately
# raise as fatal errors
# 0: All files parsed and valid PDF/A
# 1: All files parsed, some invalid PDF/A.
#    The files might still be valid PDFs, just not A format
# 7: Failed to parse one or more files.
#    The files are somehow broken/invalid PDFs
OK_CODES = [0, 1, 7]


class VerapdfExtractor(BaseExtractor):
    """PDF/A extractor."""

    # Supported mimetypes and versions
    _supported_metadata = [VerapdfMeta]
    _only_wellformed = True  # Only well-formed check

    def scrape_file(self):
        """
        Scrape file.

        :raises: VeraPDFError
        """
        # --nonpdfext flag allows also files without the .pdf extension
        shell = Shell(["verapdf",
                      self.filename, "--nonpdfext"])

        if shell.returncode not in OK_CODES:
            self._errors.append(
                f"VeraPDF returned invalid return code: {shell.returncode}")
            self._errors.append(shell.stderr)
            self._check_supported()
            return

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

                    # Here we can be sure that the final report has been
                    # generated and file is PDF/A compliant. If also the return
                    # code is 0, we can be sure that everything went well.
                    # Stderr output might still contain logged warnings about
                    # the file contents, so append stderr to messages to catch
                    # potentially useful information. If the returncode is not
                    # 0, be safe and dump stderr in errors.
                    if shell.returncode == 0:
                        self._messages.append(shell.stderr)
                    else:
                        self._errors.append(shell.stderr)

                profile = \
                    report.xpath("//validationReport")[0].get("profileName")
            else:
                self._errors.append(shell.stdout)
        except ET.XMLSyntaxError:
            self._errors.append(shell.stderr)

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, profile=profile))

        self._check_supported()

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        tool_shell = Shell(["verapdf", "--version"])

        """
        Find verPDF string and capture a group after it containing
        integers and dots until any other character appears.
        """
        regex = r"veraPDF ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex, tool_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not find VeraPDF version. stdout: %s, stderr: %s",
                tool_shell.stdout, tool_shell.stderr,
                exc_info=True,
            )
            version = UNAV
        return {"veraPDF": {"version": version}}
