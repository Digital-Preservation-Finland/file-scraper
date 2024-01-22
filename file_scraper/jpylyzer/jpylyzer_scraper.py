""""Scraper for jp2 files using Jpylyzer."""
try:
    from jpylyzer import jpylyzer
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.jpylyzer.jpylyzer_model import JpylyzerMeta
from file_scraper.utils import decode_path


class JpylyzerScraper(BaseScraper):
    """Scraper to check the wellformedness of jp2 files."""
    _supported_metadata = [JpylyzerMeta]
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape data from file."""
        result = jpylyzer.checkOneFile(decode_path(self.filename))
        well_formed = result.findtext("./isValid")
        if well_formed == "True":
            self._messages.append("File is well-formed and valid.")
        else:
            self._errors.append("Failed: document is not well-formed.")
        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_mime=True, allow_unav_version=True,
                              allow_unap_version=True)
