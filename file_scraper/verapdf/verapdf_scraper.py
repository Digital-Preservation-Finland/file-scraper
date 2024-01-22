"""PDF/A scraper."""

try:
    import lxml.etree as ET
except ImportError:
    pass

import distutils.spawn
from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.config import get_value
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
        verapdf_loc = get_value("VERAPDF_PATH")
        if distutils.spawn.find_executable("verapdf") is not None:
            verapdf_loc = "verapdf"
        # --nonpdfext flag allows also files without the .pdf extension
        cmd = [verapdf_loc, encode_path(self.filename), "--nonpdfext"]
        shell = Shell(cmd)

        if shell.returncode not in OK_CODES:
            self._errors.append("VeraPDF returned invalid return code: %s"
                                % shell.returncode)
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
