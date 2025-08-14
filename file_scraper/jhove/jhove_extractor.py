"""Extractor for gif, html, jpeg, tif, pdf and wav files using JHove."""
from pathlib import Path

try:
    import lxml.etree
except ImportError:
    pass
import re

from file_scraper.base import BaseExtractor
from file_scraper.shell import Shell
from file_scraper.defaults import UNAV
from file_scraper.logger import LOGGER
from file_scraper.jhove.jhove_model import (JHoveAiffMeta, JHoveDngMeta,
                                            JHoveEpubMeta, JHoveGifMeta,
                                            JHoveHtmlMeta, JHoveJpegMeta,
                                            JHovePdfMeta, JHoveTiffMeta,
                                            JHoveUtf8Meta, JHoveWavMeta,
                                            get_field)


class JHoveExtractorBase(BaseExtractor):
    """Scraping methods for all specific JHove extractors."""

    _supported_metadata = []
    _jhove_module = None
    _only_wellformed = True

    def __init__(self, filename: Path, mimetype, version=None, params=None):
        """
        Initialize JHove base scarper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters needed for the extractor
        """
        self._report = None  # JHove report
        super().__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    def extract(self):
        """Run JHove command and store XML output to self.report."""

        shell = Shell(["jhove", "-h",
                       "XML", "-m", self._jhove_module, self.filename])

        if shell.returncode != 0:
            self._errors.append(
                f"JHove returned invalid return code: {shell.returncode}\n"
                f"{shell.stderr}")
        self._report = lxml.etree.fromstring(shell.stdout_raw)

        status = get_field(self._report, "status")
        self._messages.append(status)
        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.append(shell.stdout)
            self._errors.append(shell.stderr)

        self.streams = list(self.iterate_models(
            well_formed=self.well_formed, report=self._report))

        self._check_supported(allow_unav_version=True,
                              allow_unap_version=True)

    def tools(self):
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


class JHoveGifExtractor(JHoveExtractorBase):
    """Variables for scraping gif files."""

    _jhove_module = "GIF-hul"
    _supported_metadata = [JHoveGifMeta]


class JHoveHtmlExtractor(JHoveExtractorBase):
    """Variables for scraping html files."""

    _jhove_module = "HTML-hul"
    _supported_metadata = [JHoveHtmlMeta]

    def extract(self):
        """
        Scrape the file.

        Check the character encoding declaration additionally. JHove HTML
        module seems to check only the declaration or metadata elements from
        the (X)HTML file, and these are optional in practice. If these are
        missing, then we just need to rely on other extractor tools.
        """
        super().extract()

        # self.streams is empty if MIME type is not supported.
        # We run _check_supported() in super() where this case
        # is handled by giving an error message.
        if not self.streams:
            return
        if not self._params.get("charset", None):
            self._errors.append("Character encoding not defined.")
            return
        encoding = self.streams[0].charset()
        if encoding is not None and \
                encoding.upper() != self._params["charset"]:
            self._errors.append(
                f"Found encoding declaration {encoding} from the file "
                f"{self.filename}, but {self._params['charset']} was "
                f"expected.")


class JHoveJpegExtractor(JHoveExtractorBase):
    """Variables for scraping jpeg files."""

    _jhove_module = "JPEG-hul"
    _supported_metadata = [JHoveJpegMeta]


class JHoveTiffExtractor(JHoveExtractorBase):
    """Variables for scraping tiff files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveTiffMeta]


class JHovePdfExtractor(JHoveExtractorBase):
    """PDF extractor using JHove."""

    _jhove_module = "PDF-hul"
    _supported_metadata = [JHovePdfMeta]

    def extract(self):
        """
        Scrape the file, and check and log PDF root version.

        JHove does not support PDF 1.7, but it can detect it. Thus if PDF 1.7
        is detected, any possible errors JHove might detect will be
        disregarded. Regardless of what version is detected, the PDF root
        version is logged in messages, which is useful for PDF-A file scraping.
        """

        super().extract()

        if self.streams:
            mimetype = self.streams[0].mimetype()
            version = self.streams[0].version()

            if mimetype == "application/pdf":
                if version == "1.7":
                    self._errors = []
                    self._messages = ["JHove does not support PDF 1.7: "
                                      "All errors and messages ignored."]

                self._messages.append(f"PDF root version is {version}")


class JHoveWavExtractor(JHoveExtractorBase):
    """Variables for scraping wav files."""

    _jhove_module = "WAVE-hul"
    _supported_metadata = [JHoveWavMeta]

    def extract(self):
        """
        Scrape file.
        Add extra error message, if RF64 profile used.
        """
        super().extract()
        if "RF64" in get_field(self._report, "profile"):
            self._errors.append("RF64 is not a supported format")


class JHoveUtf8Extractor(JHoveExtractorBase):
    """
    Extractor for checking wether a text file is a valid UTF-8 file.

    We don't want to run this for all files, but just for UTF-8 text files
    separately. This must be run after actual scraping, since we have to know
    the charset of the file.
    """
    _jhove_module = "UTF8-hul"
    _supported_metadata = [JHoveUtf8Meta]

    def _check_supported(self, allow_unav_mime=False,
                         allow_unav_version=False,
                         allow_unap_version=False):
        """Do nothing: we dont care about the mimetype or version."""

    def iterate_models(self, **kwargs):
        """
        Iterate extractor models and create streams.

        We need to override this since _supported attribute is empty and
        the extractor is run differenty.
        """
        yield self._supported_metadata[0](**kwargs)


class JHoveEpubExtractor(JHoveExtractorBase):
    """Variables for scraping EPUB files."""

    _jhove_module = "EPUB-ptc"
    _supported_metadata = [JHoveEpubMeta]


class JHoveDngExtractor(JHoveExtractorBase):
    """Variables for scraping dng files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveDngMeta]


class JHoveAiffExtractor(JHoveExtractorBase):
    """Variables for scraping AIFF files."""

    _jhove_module = "AIFF-hul"
    _supported_metadata = [JHoveAiffMeta]
