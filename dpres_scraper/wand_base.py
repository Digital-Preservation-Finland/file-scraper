"""Metadata scraper for image file formats"""
try:
    import wand.image
except ImportError:
    pass

from dpres_scraper.base import BaseScraper


class Wand(BaseScraper):
    """Scraper class for collecting image metadata
    """

    def __init__(self, filename, mimetype, validation=True, params={}):
        """Initialize scraper
        """
        self._wand_index = None
        self._wand_stream = None
        self._wand = None
        super(Wand, self).__init__(filename, mimetype, validation, params)

    def scrape_file(self):
        """Scrape data from file
        """
        try:
            self._wand = wand.image.Image(filename=self.filename)
        except:
            self.errors('Error in scraping file.')
        else:
            self.messages('The file was scraped.')
        finally:
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """Iterate image streams
        """
        if stream_type in [None, 'image']:
            for index, stream in enumerate(self._wand.sequence):
                self._wand_stream = stream
                self._wand_index = index
                yield stream

    def set_tool_stream(self, index):
        """Set image stream
        """
        self._wand_index = index
        self._wand_stream = self._wand.sequence[index]

    # pylint: disable=no-self-use
    def _s_version(self):
        """Return version of file
        """
        return None

    # pylint: disable=no-self-use
    def _s_stream_type(self):
        """Return stream type
        """
        return 'image'

    def _s_index(self):
        """Return stream index
        """
        return self._wand_index

    def _s_colorspace(self):
        """Returns colorspace
        """
        if self._wand_stream.colorspace is not None:
            return self._wand_stream.colorspace
        return None

    def _s_width(self):
        """Returns image width
        """
        if self._wand_stream.width is not None:
            return str(self._wand_stream.width)
        return None

    def _s_height(self):
        """Returns image height
        """
        if self._wand_stream.height is not None:
            return str(self._wand_stream.height)
        return None

    def _s_bps_value(self):
        """Returns bits per sample
        """
        if self._wand_stream.depth is not None:
            return str(self._wand_stream.depth)
        return None

    # pylint: disable=no-self-use
    def _s_bps_unit(self):
        """Returns sample unit
        """
        return None

    def _s_compression(self):
        """Returns compression scheme
        """
        if self._wand.compression is not None:
            return self._wand.compression
        return None

    # pylint: disable=no-self-use
    def _s_byte_order(self):
        """Returns byte order
        """
        return None

    # pylint: disable=no-self-use
    def _s_samples_per_pixel(self):
        """Returns samples per pixel
        """
        return None
