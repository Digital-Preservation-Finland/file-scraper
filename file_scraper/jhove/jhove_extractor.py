"""Extractor for gif, html, jpeg, tif, pdf and wav files using JHove."""
from __future__ import annotations

from typing import Literal, TypeVar

try:
    import lxml.etree
except ImportError:
    pass
import re

from file_scraper.base import BaseExtractor
from file_scraper.defaults import UNAV
from file_scraper.jhove.jhove_model import (
    JHoveAiffMeta,
    JHoveBaseMeta,
    JHoveDngMeta,
    JHoveEpubMeta,
    JHoveGifMeta,
    JHoveHtmlMeta,
    JHoveJpegMeta,
    JHovePdfMeta,
    JHoveTiffMeta,
    JHoveUtf8Meta,
    JHoveWavMeta,
    get_field,
)
from file_scraper.logger import LOGGER
from file_scraper.shell import Shell

JHoveMetaT = TypeVar("JHoveMetaT", bound=JHoveBaseMeta)


class JHoveExtractorBase(BaseExtractor[JHoveMetaT]):
    """Scraping methods for all specific JHove extractors."""

    _jhove_module = None
    _only_wellformed = True

    _allow_unav_version = True
    _allow_unap_version = True

    def _base_extract(self) -> lxml.etree._Element:
        """Run JHove command and return XML output."""
        shell = Shell(["jhove", "-h",
                       "XML", "-m", self._jhove_module, self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"JHove returned invalid return code: {shell.returncode}\n"
                f"{shell.stderr}")
        report = lxml.etree.fromstring(shell.stdout_raw)

        status = get_field(report, "status")
        self._messages.append(status)
        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.append(shell.stdout)
            self._errors.append(shell.stderr)

        self.streams = list(
            self.iterate_models(
                well_formed=self.well_formed,
                report=report,
            )
        )
        return report

    def _extract(self) -> None:
        self._base_extract()

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        version_shell = Shell(["jhove"])

        regex_jhove = r"App:[\n ]+API: ([\d\.]+)"
        try:
            version = next(
                re.finditer(regex_jhove, version_shell.stdout, re.MULTILINE)
                ).groups()[0]
        except StopIteration:
            LOGGER.warning(
                "Could not retrieve JHOVE version from stdout: %s",
                version_shell.stdout
            )
            version = UNAV

        return {"JHOVE": {
            "version": version
            }
        }


class JHoveGifExtractor(JHoveExtractorBase[JHoveGifMeta]):
    """Variables for scraping gif files."""

    _jhove_module = "GIF-hul"
    _supported_metadata = [JHoveGifMeta]


class JHoveHtmlExtractor(JHoveExtractorBase[JHoveHtmlMeta]):
    """Variables for scraping html files."""

    _jhove_module = "HTML-hul"
    _supported_metadata = [JHoveHtmlMeta]

    def _extract(self) -> None:
        """
        Scrape the file.

        Check the character encoding declaration additionally. JHove HTML
        module seems to check only the declaration or metadata elements from
        the (X)HTML file, and these are optional in practice. If these are
        missing, then we just need to rely on other extractor tools.
        """
        super()._extract()

        # self.streams is empty if MIME type is not supported.
        # We run _validate() in super() where this case
        # is handled by giving an error message.
        if not self.streams:
            return
        if not self._predefined_charset:
            self._errors.append("Character encoding not defined.")
            return
        encoding = self.streams[0].charset()
        if encoding is not None \
                and encoding != self._predefined_charset:
            self._errors.append(
                f"Found encoding declaration {encoding} from the file "
                f"{self.filename}, but {self._predefined_charset} was "
                f"expected.")


class JHoveJpegExtractor(JHoveExtractorBase[JHoveJpegMeta]):
    """Variables for scraping jpeg files."""

    _jhove_module = "JPEG-hul"
    _supported_metadata = [JHoveJpegMeta]


class JHoveTiffExtractor(JHoveExtractorBase[JHoveTiffMeta]):
    """Variables for scraping tiff files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveTiffMeta]

    # JHove error codes that will be ignored
    # This is used for GeoTIFF 1.1 files, which JHove thinks are invalid
    ignored_error_ids = {
        "TIFF-HUL-66",  # ProjectedCSType out of range
    }

    def _base_extract(self) -> lxml.etree._Element:
        """Run JHove command and return XML output."""
        shell = Shell(
            ["jhove", "-h", "XML", "-m", self._jhove_module, self.filename]
        )

        if shell.returncode != 0:
            self._errors.append(
                f"JHove returned invalid return code: {shell.returncode}\n"
                f"{shell.stderr}"
            )
        report = lxml.etree.fromstring(shell.stdout_raw)

        profile = get_field(report, "profile")

        if profile and "Baseline GeoTIFF 1" in profile:
            real_errors, status = self._filter_and_update_report(report)
        else:
            status = get_field(report, "status")
            real_errors = []

        self._messages.append(status)

        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.extend(real_errors)
            self._errors.append(shell.stdout)
            self._errors.append(shell.stderr)

        self.streams = list(
            self.iterate_models(
                well_formed=self.well_formed,
                report=report,
            )
        )
        return report

    def _filter_and_update_report(
        self, report: lxml.etree._Element
    ) -> tuple[list[str], str]:
        """Filter JHove errors messages that should be ignored and update the
        JHove XML report.

        :param report: JHove report.
        :returns: Tuple with list of real errors and status.
        """
        real_errors = []
        messages_to_remove = []

        # Filter JHove messages and collect real errors
        for message in report.findall(".//{*}message"):
            severity = message.attrib.get("severity")
            msg_id = message.attrib.get("id")
            text = message.text or ""

            if msg_id in self.ignored_error_ids:
                messages_to_remove.append(message)
                continue

            if severity == "error":
                real_errors.append(text)

        # Remove errors that should be ignored from the report
        for msg in messages_to_remove:
            parent = msg.getparent()
            if parent is not None:
                parent.remove(msg)

        # EPSG check
        epsg = self._get_epsg(report)
        if epsg is None:
            real_errors.append("EPSG code not found")
        elif not self._valid_epsg(epsg):
            real_errors.append("Invalid EPSG code")

        status_text = self._update_status(report, real_errors)

        return real_errors, status_text

    @staticmethod
    def _update_status(
        report: lxml.etree._Element, real_errors: list[str]
    ) -> str:
        """Update status of the XML report and return it."""
        status_elem = report.find(".//{*}status")
        status_text = get_field(report, "status")

        if not real_errors:
            # No real errors, make sure status is valid
            new_status = "Well-Formed and valid"

            if status_elem is not None:
                status_elem.text = new_status

            status_text = new_status
        elif "Well-Formed" in status_text:
            # Real errors, make sure status is not valid
            new_status = "Well-Formed, but not valid"

            if status_elem is not None:
                status_elem.text = new_status

            status_text = new_status

        return status_text

    @staticmethod
    def _get_epsg(report: lxml.etree._Element) -> str | None:
        """Find EPSG code from JHove report."""
        elem = report.find(
            ".//{*}property[{*}name='ProjectedCSType']/{*}values/{*}value"
        )
        if elem is not None:
            return elem.text
        return None

    @staticmethod
    def _valid_epsg(epsg: str) -> bool:
        """Check that EPSG is a positive integer."""
        try:
            value = int(epsg)
            return str(value) == epsg and value > 0
        except (ValueError, TypeError):
            return False


class JHovePdfExtractor(JHoveExtractorBase[JHovePdfMeta]):
    """PDF extractor using JHove."""

    _jhove_module = "PDF-hul"
    _supported_metadata = [JHovePdfMeta]

    def _extract(self) -> None:
        """
        Scrape the file, and check and log PDF root version.

        JHove does not support PDF 1.7, but it can detect it. Thus if PDF 1.7
        is detected, any possible errors JHove might detect will be
        disregarded. Regardless of what version is detected, the PDF root
        version is logged in messages, which is useful for PDF-A file scraping.
        """

        super()._extract()

        if self.streams:
            mimetype = self.streams[0].mimetype()
            version = self.streams[0].version()

            if mimetype == "application/pdf":
                if version == "1.7":
                    self._errors = []
                    self._messages = ["JHove does not support PDF 1.7: "
                                      "All errors and messages ignored."]

                self._messages.append(f"PDF root version is {version}")


class JHoveWavExtractor(JHoveExtractorBase[JHoveWavMeta]):
    """Variables for scraping wav files."""

    _jhove_module = "WAVE-hul"
    _supported_metadata = [JHoveWavMeta]

    def _extract(self) -> None:
        """
        Scrape file.
        Add extra error message, if RF64 profile used.
        """
        report = self._base_extract()
        if "RF64" in get_field(report, "profile"):
            self._errors.append("RF64 is not a supported format")


class JHoveUtf8Extractor(JHoveExtractorBase[JHoveUtf8Meta]):
    """
    Extractor for checking wether a text file is a valid UTF-8 file.

    We don't want to run this for all files, but just for UTF-8 text files
    separately. This must be run after actual scraping, since we have to know
    the charset of the file.
    """
    _jhove_module = "UTF8-hul"
    _supported_metadata = [JHoveUtf8Meta]

    def _validate(self):
        """Do nothing: we dont care about the mimetype or version."""

    @property
    def well_formed(self) -> Literal[False] | None:
        """Return well-formedness status of the scraped file.

        This extractor validates only the file encoding, so some other
        extractor must validate the syntax. Therefore, this method will
        never return `True`.

        :returns: False if encoding is OK None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def iterate_models(self, **kwargs):
        """
        Iterate extractor models and create streams.

        We need to override this since _supported attribute is empty and
        the extractor is run differenty.
        """
        yield self._supported_metadata[0](**kwargs)


class JHoveEpubExtractor(JHoveExtractorBase[JHoveEpubMeta]):
    """Variables for scraping EPUB files."""

    _jhove_module = "EPUB-ptc"
    _supported_metadata = [JHoveEpubMeta]


class JHoveDngExtractor(JHoveExtractorBase[JHoveDngMeta]):
    """Variables for scraping dng files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveDngMeta]


class JHoveAiffExtractor(JHoveExtractorBase[JHoveAiffMeta]):
    """Variables for scraping AIFF files."""

    _jhove_module = "AIFF-hul"
    _supported_metadata = [JHoveAiffMeta]
