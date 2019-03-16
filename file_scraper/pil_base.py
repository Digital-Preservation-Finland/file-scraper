"""Metadata scraper for image file formats"""
try:
    import PIL.Image
except ImportError:
    pass

from file_scraper.base import BaseScraper


SAMPLES_PER_PIXEL = {'1': '1', 'L': '1', 'P': '1', 'RGB': '3', 'YCbCr': '3',
                     'LAB': '3', 'HSV': '3', 'RGBA': '4', 'CMYK': '4',
                     'I': '1', 'F': '1'}


class Pil(BaseScraper):
    """Scraper class for collecting image metadata
    """

    def __init__(self, filename, mimetype, validation=True, params=None):
        """Initialize scraper
        :filename: File path
        :mimetype: Predicted mimetype of the file
        :validation: True for the full validation, False for just
                     identification and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._pil = None        # Pil result
        self._pil_index = None  # Current index in Pil result
        super(Pil, self).__init__(filename, mimetype, validation, params)

    def scrape_file(self):
        """Scrape data from file.
        """
        try:
            self._pil = PIL.Image.open(self.filename)
        except:
            self.errors('Error in scraping file.')
        else:
            self.messages('The file was scraped successfully.')
        finally:
            self._check_supported()
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """Iterate image streams
        :stream_type: Only image streams are allowed.
        """
        if stream_type in [None, 'image']:
            if not hasattr(self._pil, 'n_frames'):
                self._pil_index = 0
                yield self._pil
            else:
                for index in range(0, self._pil.n_frames):
                    self._pil.seek(index)
                    self._pil_index = index
                    yield self._pil

    def set_tool_stream(self, index):
        """Set image stream with given index
        :index: stream index
        """
        self._pil.seek(index)
        self._pil_index = index

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
        return self._pil_index

    def _s_colorspace(self):
        """Returns colorspace
        """
        return None

    def _s_width(self):
        """Returns image width
        """
        if self._pil.width is not None:
            return str(self._pil.width)
        return None

    def _s_height(self):
        """Returns image height
        """
        if self._pil.height is not None:
            return str(self._pil.height)
        return None

    def _s_bps_value(self):
        """Returns bits per sample
        """
        return None

    def _s_bps_unit(self):
        """Returns sample unit
        """
        if self._pil.mode == 'F':
            return 'floating point'
        else:
            return 'integer'

    def _s_compression(self):
        """Returns compression scheme
        """
        return None

    # pylint: disable=no-self-use
    def _s_byte_order(self):
        """Returns byte order
        """
        return None

    def _s_samples_per_pixel(self):
        """Returns samples per pixel
        """
        return SAMPLES_PER_PIXEL[self._pil.mode]
