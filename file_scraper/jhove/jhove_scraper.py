"""Scraper for gif, html, jpeg, tif, pdf and wav files using JHove."""
from __future__ import unicode_literals

try:
    import lxml.etree
except ImportError:
    pass

from file_scraper.base import BaseScraper, ProcessRunner
from file_scraper.jhove.jhove_model import (JHoveGifMeta, JHoveHtmlMeta,
                                            JHoveJpegMeta, JHoveTiffMeta,
                                            JHovePdfMeta, JHoveWavMeta,
                                            JHoveUtf8Meta, get_field)
from file_scraper.utils import ensure_text


class JHoveScraperBase(BaseScraper):
    """Scraping methods for all specific JHove scrapers."""

    _supported_metadata = []
    _jhove_module = None
    _only_wellformed = True
    _force_metadata_use = False  # Skip checking if metadata model is supported

    def __init__(self, filename, check_wellformed=True, params=None):
        """
        Initialize JHove base scarper.

        :filename: File path
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._report = None  # JHove report
        self._shell = None  # ProcessRunner object
        super(JHoveScraperBase, self).__init__(filename, check_wellformed,
                                               params)

    def scrape_file(self):
        """Run JHove command and store XML output to self.report."""
        if not self._check_wellformed and self._only_wellformed:
            self._messages.append("Skipping scraper: Well-formed check not"
                                  "used.")
            return

        exec_cmd = ["jhove", "-h", "XML", "-m",
                    self._jhove_module, self.filename]
        self._shell = ProcessRunner(exec_cmd)

        if self._shell.returncode != 0:
            self._errors.append("JHove returned error: %s\n%s" % (
                self._shell.returncode, ensure_text(self._shell.stderr)))

        self._report = lxml.etree.fromstring(self._shell.stdout)

        status = get_field(self._report, "status")
        self._messages.append(status)
        if "Well-Formed and valid" not in status:
            self._errors.append("Validator returned error.")
            self._errors.append(ensure_text(self._shell.stdout))
            self._errors.append(ensure_text(self._shell.stderr))

        # If the MIME type is forced, use that, otherwise scrape the MIME type
        if self._given_mimetype:
            mimetype = self._given_mimetype
        else:
            mimetype = get_field(self._report, "mimeType")

        if mimetype == "text/xml":  # XML MIME type has to be set manually
            mimetype = "application/xhtml+xml"
        elif mimetype is not None and "audio/vnd.wave" in mimetype:  # wav also
            mimetype = "audio/x-wav"

        for md_class in self._supported_metadata:
            if md_class.is_supported(mimetype) or self._force_metadata_use:
                self.streams.append(md_class(self._report, self._errors,
                                             self._given_mimetype,
                                             self._given_version))

        self._check_supported(allow_unav_version=True)


class JHoveGifScraper(JHoveScraperBase):
    """Variables for scraping gif files."""

    _jhove_module = "GIF-hul"
    _supported_metadata = [JHoveGifMeta]


class JHoveHtmlScraper(JHoveScraperBase):
    """Variables for scraping html files."""

    _jhove_module = "HTML-hul"
    _supported_metadata = [JHoveHtmlMeta]


class JHoveJpegScraper(JHoveScraperBase):
    """Variables for scraping jpeg files."""

    _jhove_module = "JPEG-hul"
    _supported_metadata = [JHoveJpegMeta]


class JHoveTiffScraper(JHoveScraperBase):
    """Variables for scraping tiff files."""

    _jhove_module = "TIFF-hul"
    _supported_metadata = [JHoveTiffMeta]


class JHovePdfScraper(JHoveScraperBase):
    """Variables for scraping pdf files."""

    _jhove_module = "PDF-hul"
    _supported_metadata = [JHovePdfMeta]


class JHoveWavScraper(JHoveScraperBase):
    """Variables for scraping wav files."""

    _jhove_module = "WAVE-hul"
    _supported_metadata = [JHoveWavMeta]


class JHoveUtf8Scraper(JHoveScraperBase):
    """
    Scraper for checking wether a text file is a valid UTF-8 file.

    We don't want to run this for all files, but just for UTF-8 text files
    separately. This must be run after actual scraping, since we have to know
    the charset of the file.
    """
    _jhove_module = "UTF8-hul"
    _supported_metadata = [JHoveUtf8Meta]
    _force_metadata_use = True

    def _check_supported(self, allow_unav_mime=False,
                         allow_unav_version=False,
                         allow_unap_version=False):
        """Do nothing: we dont care about the mimetype or version."""
        pass
