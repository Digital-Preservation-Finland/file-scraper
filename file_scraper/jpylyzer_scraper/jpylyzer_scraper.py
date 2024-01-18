""""Scraper for jp2 files using Jpylyzer."""
try:
    import jpylyzer
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.jpylyzer.jpylyzer_model import JpylyzerMeta


class JpylyzerScraper(BaseScraper):
    """Scraper to check the wellformedness of jp2 files."""
    _supported_metadata = [JpylyzerMeta]
    _only_wellformed = True   # Only well-formed check

    def scrape_file(self):
        """Scrape data from file."""
        result = jpylyzer.checkOneFile(self.filename)
        well_formed = result.findtext("./isValid")
        if not well_formed:
            self._errors.append("Failed: document is not well-formed.")
