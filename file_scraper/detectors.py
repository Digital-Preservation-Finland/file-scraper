"""File format detectors."""
# pylint: disable=ungrouped-imports

import ctypes

try:
    from file_scraper.defaults import MAGIC_LIBRARY
    ctypes.cdll.LoadLibrary(MAGIC_LIBRARY)
except OSError:
    print('%s not found, MS Office detection may not work properly if '
          'file command library is older.' % MAGIC_LIBRARY)

import magic
from fido.fido import Fido, defaults
from fido.pronomutils import get_local_pronom_versions
from file_scraper.base import BaseDetector
from file_scraper.defaults import PRONOM_DICT, MIMETYPE_DICT, VERSION_DICT, \
    PRIORITY_PRONOM
from file_scraper.utils import encode


class _FidoReader(Fido):
    """Fido wrapper to get pronom code, mimetype and version."""

    # Global variable in Fido
    # pylint: disable=invalid-name, global-statement
    # pylint: disable=global-variable-not-assigned
    global defaults

    def __init__(self, filename):
        """
        Initialize the reader.

        Fido is done with old-style python and does not inherit object,
        so super() is not available.
        :filename: File path
        """
        self.filename = filename  # File path
        self.puid = None          # Identified pronom code
        self.mimetype = None      # Identified mime type
        self.version = None       # Identified file format version
        Fido.__init__(self, quiet=True, format_files=[
            'formats-v94.xml', 'format_extensions.xml'])

    def identify(self):
        """Identify file format with using pronom registry."""
        versions = get_local_pronom_versions()
        defaults['xml_pronomSignature'] = versions.pronom_signature
        defaults['containersignature_file'] = \
            versions.pronom_container_signature
        defaults['xml_fidoExtensionSignature'] = \
            versions.fido_extension_signature
        defaults['format_files'] = [defaults['xml_pronomSignature']]
        defaults['format_files'].append(
            defaults['xml_fidoExtensionSignature'])
        self.identify_file(filename=self.filename, extension=False)

    def print_matches(self, fullname, matches, delta_t, matchtype=''):
        """Get puid, mimetype and version.

        :fullname: File path
        :matches: Matches tuples in Fido
        :delta_t: Not needed here, but originates from Fido
        :matchtype: Not needed here, but originates from Fido
        """
        # pylint: disable=unused-argument
        for (item, _) in matches:
            self.puid = self.get_puid(item)
            if self.puid in PRONOM_DICT:
                (self.mimetype, self.version) = PRONOM_DICT[self.puid]
                return

        for (item, _) in matches:
            self.puid = self.get_puid(item)
            if self.puid in PRIORITY_PRONOM:
                self._find_mime(item)
                return

        for (item, _) in matches:
            if self.mimetype is None:
                self.puid = self.get_puid(item)
                self._find_mime(item)

    def _find_mime(self, item):
        """Find mimetype and version in Fido.

        :item: Fido result
        """
        mime = item.find('mime')
        self.mimetype = mime.text if mime is not None else None
        version = item.find('version')
        self.version = version.text if version is not None else None
        if self.mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[self.mimetype]
        if self.mimetype in VERSION_DICT:
            if self.version in VERSION_DICT[self.mimetype]:
                self.version = \
                    VERSION_DICT[self.mimetype][self.version]


class FidoDetector(BaseDetector):
    """Fido detector."""

    def detect(self):
        """Detect file format and version."""
        fido = _FidoReader(self.filename)
        fido.identify()
        self.mimetype = fido.mimetype
        self.version = fido.version
        self.info = {'class': self.__class__.__name__,
                     'messages': '',
                     'errors': ''}

    def get_important(self):
        """Return important mime types.

        :returns: Mime type
        """
        important = {}
        if self.mimetype not in [
                None,
                'text/html',
                'application/zip']:
            important['mimetype'] = self.mimetype
        return important


class MagicDetector(BaseDetector):
    """File magic detector."""

    def detect(self):
        """Detect mimetype."""
        magic_ = magic.open(magic.MAGIC_MIME_TYPE)
        magic_.load()
        mimetype = magic_.file(encode(self.filename))
        magic_.close()
        if mimetype in MIMETYPE_DICT:
            self.mimetype = MIMETYPE_DICT[mimetype]
        else:
            self.mimetype = mimetype
        self.info = {'class': self.__class__.__name__,
                     'messages': '',
                     'errors': ''}

    def get_important(self):
        """
        Important mime types.

        :returns: Mime type
        """
        important = {}
        if self.mimetype in [
                'application/x-internet-archive',
                'application/vnd.oasis.opendocument.formula']:
            important['mimetype'] = self.mimetype
        return important
