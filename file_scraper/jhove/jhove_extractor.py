"""Extractor for gif, html, jpeg, tif, pdf and wav files using JHove."""
from __future__ import annotations

from dataclasses import dataclass
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

        return shell.stdout, shell.stderr, report

    def _base_analyze_report(self, stdout: str, stderr: str,
                             report: lxml.etree._Element) -> None:
        """Analyze JHove report and log status and potential errors"""
        status = get_field(report, "status")
        self._messages.append(status)
        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.append(stdout)
            self._errors.append(stderr)

    def _base_streams_output(self, report: lxml.etree._Element) -> None:
        """Add results to streams"""
        self.streams = list(
            self.iterate_models(
                well_formed=self.well_formed,
                report=report,
            )
        )

    def _extract(self) -> None:
        stdout, stderr, report = self._base_extract()
        self._base_analyze_report(stdout, stderr, report)
        self._base_streams_output(report)

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
    """Variables for scraping TIFF and GeoTIFF files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveTiffMeta]

    # pylint: disable=too-few-public-methods
    class _IgnoredError:
        """Simple class for handling JHove errors we want to ignore"""

        def __init__(self, err_id: str, err_msg: str, err_reason: str) -> None:
            self.id = err_id
            self.msg = err_msg
            self.reason = err_reason

        def __repr__(self):
            return f"{self.msg} (reason: {self.reason})"

    @dataclass
    class CRSInfo:
        """Dataclass to store Coordinate Reference System info. CRS should
        contain either projected CRS or geodetic CRS, and an optional
        supplementary vertical CRS.

        More info: https://docs.ogc.org/is/19-008r4/19-008r4.html#_requirements_for_definition_of_model_crs_when_model_is_from_geotiff_crs_register

        :var projected: EPSG Projected CRS code.
        :var geodetic: EPSG Geographic 2D **or** Geocentric CRS code.
        :var vertical: EPSG Vertical CRS **or** EPSG Geographic 3D CRS code.
        """

        projected: str | None
        geodetic: str | None
        vertical: str | None

        def valid(self) -> bool:
            """Check either projected or geodetic CRS is defined, but not both
            at the same time.
            """
            return (self.projected is not None) ^ (self.geodetic is not None)

    # This is used for GeoTIFF 1.1 files, which JHove thinks are invalid
    ignored_errors = [
        _IgnoredError(
            "TIFF-HUL-66",
            "ProjectedCSType value out of range",
            "not relevant for OGC GeoTIFF 1.1",
        )
    ]

    def _extract(self) -> None:
        stdout, stderr, report = self._base_extract()
        self._tiff_analyze_report(stdout, stderr, report)
        self._base_streams_output(report)

    def _tiff_analyze_report(
        self, stdout: str, stderr: str, report: lxml.etree._Element
    ) -> None:
        """Analyze JHove report and log status and potential errors"""
        profile = get_field(report, "profile")
        filtered_errors = []
        crs_error = ""

        if profile and "Baseline GeoTIFF 1" in profile:
            status, filtered_errors, crs_error = self._check_errors(report)
        else:
            status = get_field(report, "status")

        self._messages.append(status)

        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.append(crs_error)
            self._errors.append(stdout)
            self._errors.append(stderr)
        elif filtered_errors:
            self._messages.append(
                "Found one or more errors, but they have "
                "been deemed as false positives within "
                "this framework. We'll ignore the following "
                "errors and treat the file as valid: "
                f"{filtered_errors}"
            )

    def _check_errors(
        self, report: lxml.etree._Element
    ) -> tuple[str, list[_IgnoredError], str]:
        """Filter JHove errors that should be ignored and return status and
        any errors that got filtered. Also check whether the EPSG code is valid
        and return error message if it is not.

        :param report: JHove report
        :returns: Status, any errors that got filtered, and errors related to
            the EPSG value.
        """
        filtered_errors = []
        real_errors = False

        # Filter JHove messages and catch real errors
        for message in report.findall(".//{*}message"):
            severity = message.attrib.get("severity")
            msg_id = message.attrib.get("id")
            text = message.text or ""
            ignored = False

            for error in self.ignored_errors:
                if msg_id == error.id and error.msg in text:
                    filtered_errors.append(error)
                    ignored = True
                    break

            if not ignored and severity == "error":
                real_errors = True

            # If we find even one real error, we know the file is not valid
            if real_errors:
                break

        crs_error = self._check_crs(report)
        status = get_field(report, "status")

        if not (real_errors or crs_error):
            # No real errors, status is valid
            status = "Well-Formed and valid"
        elif crs_error and "Well-Formed and valid" in status:
            # Only CRS error, status is not valid
            status = "Well-Formed, but not valid"

        return status, filtered_errors, crs_error

    def _check_crs(
        self,
        report: lxml.etree._Element,
    ) -> str:
        """Validate Coordinate Reference System (CRS).

        :param report: JHove XML report.
        :returns: CRS error or empty string.
        """
        crs_error = ""
        crs_info = self._get_crs(report)

        if not crs_info.valid():
            # Both projected and geodetic are undefined, or both are defined
            crs_error = "No CRS definition found or CRS definition is invalid."

        if ((epsg := crs_info.projected) is not None) and (
            not self._valid_epsg(epsg)
        ):
            # EPSG check, JHove doesn't check this
            crs_error = "Invalid EPSG code"

        return crs_error

    def _get_crs(self, report: lxml.etree._Element,) -> CRSInfo:
        """Find CRS info.

        :param report: JHove XML report.
        :returns: CRSInfo object.
        """
        crs_info = self.CRSInfo(None, None, None)

        projected = self._find_property(report, "ProjectedCSType")
        if projected is not None:
            crs_info.projected = projected

        geodetic = self._find_property(report, "GeographicType")
        if geodetic is not None:
            crs_info.geodetic = geodetic

        vertical = self._find_property(report, "VerticalCSType")
        if vertical is not None:
            crs_info.vertical = vertical

        return crs_info

    @staticmethod
    def _find_property(report: lxml.etree._Element, name: str) -> str | None:
        """Find a property from JHove report.

        :param report: JHove XML report.
        :param name: Name of property.
        :returns: Property value or None.
        """
        elem = report.find(
            f".//{{*}}property[{{*}}name='{name}']/{{*}}values/{{*}}value"
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
        stdout, stderr, report = self._base_extract()
        self._base_analyze_report(stdout, stderr, report)
        self._base_streams_output(report)

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
