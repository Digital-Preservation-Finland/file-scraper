"""Scraper for gif, html, jpeg, tif, pdf and wav files using JHove."""
from __future__ import unicode_literals

try:
    import lxml.etree
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.shell import Shell
from file_scraper.jhove.jhove_model import (JHoveGifMeta, JHoveHtmlMeta,
                                            JHoveJpegMeta, JHoveTiffMeta,
                                            JHovePdfMeta, JHoveWavMeta,
                                            JHoveUtf8Meta, get_field)


class JHoveScraperBase(BaseScraper):
    """Scraping methods for all specific JHove scrapers."""

    _supported_metadata = []
    _jhove_module = None
    _only_wellformed = True

    def __init__(self, filename, mimetype, version=None, params=None):
        """
        Initialize JHove base scarper.

        :filename: File path
        :mimetype: Predefined mimetype
        :version: Predefined file format version
        :params: Extra parameters needed for the scraper
        """
        self._report = None  # JHove report
        super(JHoveScraperBase, self).__init__(
            filename=filename, mimetype=mimetype, version=version,
            params=params)

    def scrape_file(self):
        """Run JHove command and store XML output to self.report."""
        exec_cmd = ["jhove", "-h", "XML", "-m",
                    self._jhove_module, self.filename]
        shell = Shell(exec_cmd)

        if shell.returncode != 0:
            self._errors.append("JHove returned error: %s\n%s" % (
                shell.returncode, shell.stderr))

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


class JHoveGifScraper(JHoveScraperBase):
    """Variables for scraping gif files."""

    _jhove_module = "GIF-hul"
    _supported_metadata = [JHoveGifMeta]


class JHoveHtmlScraper(JHoveScraperBase):
    """Variables for scraping html files."""

    _jhove_module = "HTML-hul"
    _supported_metadata = [JHoveHtmlMeta]

    def scrape_file(self):
        """
        Scrape the file.

        Check the character encoding declaration additionally. JHove HTML
        module seems to check only the declaration or metadata elements from
        the (X)HTML file, and these are optional in practice. If these are
        missing, then we just need to rely on other scraper tools.
        """
        super(JHoveHtmlScraper, self).scrape_file()

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
                "Found encoding declaration %s from the file %s, but %s "
                "was expected." % (encoding, self.filename,
                                   self._params["charset"]))


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

    def scrape_file(self):
        """
        Scrape file.
        Add extra error message, if RF64 profile used.
        """
        super(JHoveWavScraper, self).scrape_file()
        if "RF64" in get_field(self._report, "profile"):
            self._errors.append("RF64 is not a supported format")


class JHoveUtf8Scraper(JHoveScraperBase):
    """
    Scraper for checking wether a text file is a valid UTF-8 file.

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
        pass

    def iterate_models(self, **kwargs):
        """
        Iterate Scraper models and create streams.

        We need to override this since _supported attribute is empty and
        the scraper is run differenty.
        """
        yield self._supported_metadata[0](**kwargs)
