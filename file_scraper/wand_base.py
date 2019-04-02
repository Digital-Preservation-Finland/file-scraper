"""Metadata scraper for image file formats"""

try:
    import wand.image
except ImportError:
    pass

from file_scraper.base import BaseScraper
from file_scraper.utils import metadata


class Wand(BaseScraper):
    """Scraper class for collecting image metadata."""

    def __init__(self, filename, mimetype, check_wellformed=True, params=None):
        """
        Initialize scraper

        :filename: File path
        :mimetype: Predicted mimetype of the file
        :check_wellformed: True for the full well-formed check, False for just
                           detection and metadata scraping
        :params: Extra parameters needed for the scraper
        """
        self._wand_index = None   # Current wand stream index
        self._wand_stream = None  # Current wand stream
        self._wand = None         # Resulted wand streams
        super(Wand, self).__init__(filename, mimetype, check_wellformed,
                                   params)

    def scrape_file(self):
        """Scrape data from file."""
        if not self._check_wellformed and self._only_wellformed:
            self.messages('Skipping scraper: Well-formed check not used.')
            self._collect_elements()
            return
        try:
            self._wand = wand.image.Image(filename=self.filename)
        except Exception as e:  # pylint: disable=broad-except, invalid-name
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

        :stream_type: Only image streams can be iterated.
        """
        if self._wand is None:
            self.streams = {0: {'index': 0}}
            yield self.streams
        elif stream_type in [None, 'image']:
            for index, stream in enumerate(self._wand.sequence):
                self._wand_stream = stream
                self._wand_index = index
                yield stream

    def set_tool_stream(self, index):
        """
        Set image stream with given index.

        :index: Stream index
        """
        self._wand_stream = self._wand.sequence[index]
        self._wand_index = index

    @metadata()
    def _version(self):
        """Return version of file format."""
        return None

    @metadata()
    def _stream_type(self):
        """Return stream type."""
        return 'image'

    @metadata()
    def _index(self):
        """Return stream index."""
        if self._wand_index is None:
            return 0
        return self._wand_index

    @metadata()
    def _colorspace(self):
        """Return colorspace."""
        if self._wand_stream is not None and \
                self._wand_stream.colorspace is not None:
            return self._wand_stream.colorspace
        return None

    @metadata()
    def _width(self):
        """Return image width."""
        if self._wand_stream is not None and \
                self._wand_stream.width is not None:
            return str(self._wand_stream.width)
        return None

    @metadata()
    def _height(self):
        """Return image height."""
        if self._wand_stream is not None and \
                self._wand_stream.height is not None:
            return str(self._wand_stream.height)
        return None

    @metadata()
    def _bps_value(self):
        """Return bits per sample."""
        if self._wand_stream is not None and \
                self._wand_stream.depth is not None:
            return str(self._wand_stream.depth)
        return None

    # pylint: disable=no-self-use
    @metadata()
    def _bps_unit(self):
        """Return sample unit."""
        return None

    @metadata()
    def _compression(self):
        """Return compression scheme."""
        if self._wand is not None and \
                self._wand.compression is not None:
            return self._wand.compression
        return None

    @metadata()
    def _samples_per_pixel(self):
        """Return samples per pixel."""
        return None
