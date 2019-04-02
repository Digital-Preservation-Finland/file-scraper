"""Metadata scraper for image file formats."""
try:
    import wand.image
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.wand.wand_model import WandTiffMeta, WandImageMeta
#from file_scraper.scrapers.wand import TiffWand, ImageWand


class WandScraper(BaseScraper):
    """Scraper for Metadata classes using wand."""

    _supported_metadata = [WandTiffMeta, WandImageMeta]

    def is_supported(self, mimetype):
        """
        Report whether the given MIME type is supported by this scraper.

        :returns: True if any metadata model supports the given MIME type,
                  otherwise False.
        """
        return any([x.is_supported(mimetype) for x in
                    self._supported_metadata])

    def scrape_file(self):
        """
        Populate streams with supported metadata objects.

        :filename: Path to the file that is being scraped.
        """

#        mediainfo = MediaInfo().parse()
#         if not self._check_wellformed and self._only_wellformed:
#             self.messages('Skipping scraper: Well-formed check not used.')
#             self._collect_elements()
#             return
        try:
            wandresults = wand.image.Image(filename=self.filename)
        except Exception as e:  # pylint: disable=broad-except, invalid-name
            self._errors.append("Error in analyzing file")
            self._errors.append(e)
        else:
            self._messages.append("The file was analyzed successfully.")
        finally:
            pass
#            self._check_supported()
#            self._collect_elements()

        for md_class in self._supported_metadata:
            for image in wandresults.sequence:
                if not md_class.is_supported(image.container.mimetype):
                    continue
                self.streams.append(md_class(image))
