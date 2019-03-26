"""Metadata scraper for image file formats."""
try:
    import PIL.Image
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.utils import metadata

SAMPLES_PER_PIXEL = {'1': '1', 'L': '1', 'P': '1', 'RGB': '3', 'YCbCr': '3',
                     'LAB': '3', 'HSV': '3', 'RGBA': '4', 'CMYK': '4',
                     'I': '1', 'F': '1'}


class Pil(BaseScraper):
    """Scraper class for collecting image metadata."""

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper.

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._pil = None  # Pil result
        self._pil_index = None  # Current index in Pil result
        super(Pil, self).__init__(filename, mimetype, check_wellformed, params)

    def scrape_file(self):
        """Scrape data from file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        try:
            self._pil = PIL.Image.open(self.filename)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            self.errors('Error in analyzing file.')
            self.errors(str(e))
        else:
            self.messages('The file was analyzed successfully.')
        finally:
            self._check_supported()
            self._collect_elements()

    def iter_tool_streams(self, stream_type):
        """
        Iterate image streams.

        :stream_type: Only image streams are allowed.
        """
        if self._pil is None:
            yield {}
        if stream_type in [None, 'image']:
            try:
                _n_frames = self._pil.n_frames
            except (AttributeError, ValueError):
                # ValueError happens when n_frame property exists, but
                # the tile tries to extend outside of image.
                _n_frames = None
            if not _n_frames:
                self._pil_index = 0
                yield self._pil
            else:
                for index in range(0, self._pil.n_frames):
                    self._pil.seek(index)
                    self._pil_index = index
                    yield self._pil

    def set_tool_stream(self, index):
        """
        Set image stream with given index.

        :index: stream index
        """
        if self._pil is not None:
            self._pil.seek(index)
            self._pil_index = index

    @metadata()
    def _s_version(self):
        """Return version of file."""
        return None

    @metadata()
    def _s_stream_type(self):
        """Return stream type."""
        return 'image'

    @metadata()
    def _s_index(self):
        """Return stream index."""
        if self._pil_index is None:
            return 0
        return self._pil_index

    # pylint: disable=no-self-use
    @metadata()
    def _s_colorspace(self):
        """Return colorspace."""
        return None

    @metadata()
    def _s_width(self):
        """Return image width."""
        if self._pil is not None and \
                self._pil.width is not None:
            return str(self._pil.width)
        return None

    @metadata()
    def _s_height(self):
        """Return image height."""
        if self._pil is not None and \
                self._pil.height is not None:
            return str(self._pil.height)
        return None

    @metadata()
    def _s_bps_value(self):
        """Return bits per sample."""
        return None

    @metadata()
    def _s_bps_unit(self):
        """Return sample unit."""
        if self._pil is None:
            return None
        if self._pil.mode == 'F':
            return 'floating point'

        return 'integer'

    @metadata()
    def _s_compression(self):
        """Return compression scheme."""
        return None

    @metadata()
    def _s_samples_per_pixel(self):
        """Return samples per pixel."""
        if self._pil is None:
            return None
        return SAMPLES_PER_PIXEL[self._pil.mode]
