from file_scraper.base import BaseScraper

try:
    import jpylyzer
except ImportError:
    pass
    

class JpylyzerScraper(BaseScraper):

    @property
    def well_formed(self):
        """
        To do...
        """
        well_formed = self.result.findtext("./isValid")
        return well_formed
    
    def scrape_file(self):
        """Scrape data from file."""
        self.result = jpylyzer.checkOneFile(self.filename)
        