"""Metadata scraper for image file formats."""
try:
    import wand.image
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.wand.wand_model import WandTiffMeta, WandImageMeta


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
            for md_class in self._supported_metadata:
                for image in wandresults.sequence:
                    if not md_class.is_supported(image.container.mimetype):
                        continue
                    self.streams.append(md_class(image))

            # TODO moved here from finally because it doesn't make much sense
            #      to raise an exception for when analyzing the image did not
            #      work out and there are no streams so no MIME or version
            #      either. Smart or dumb?
            self._check_supported()

            self._messages.append("The file was analyzed successfully.")
