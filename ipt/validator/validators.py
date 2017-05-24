"""validator iterator for digital object validation"""

# pylint: disable=unused-import
from ipt.validator.basevalidator import BaseValidator
from ipt.validator.jhove import JHoveBase, JHovePDF, \
    JHoveTiff, JHoveJPEG, JHoveHTML, JHoveGif, JHoveTextUTF8
from ipt.validator.dummytextvalidator import DummyTextValidator
from ipt.validator.xmllint import Xmllint
from ipt.validator.warctools import WarctoolsWARC, WarctoolsARC
from ipt.validator.ghost_script import GhostScript
from ipt.validator.pngcheck import Pngcheck
from ipt.validator.csv_validator import PythonCsv
from ipt.validator.ffmpeg import FFMpeg
from ipt.validator.office import Office
from ipt.validator.file import File
from ipt.validator.imagemagick import ImageMagick
from ipt.validator.pspp import PSPP


def iter_validators(fileinfo):
    """
    Find a validator for digital object from given `fileinfo` record.
    :returns: validator class

    Implementation of class factory pattern from
    http://stackoverflow.com/questions/456672/class-factory-in-python
    """

    # pylint: disable=no-member

    found_validator = False

    if fileinfo.get("erroneous-mimetype", False):
        validator = UnknownFileformat(fileinfo)
        yield validator
        return

    for cls in BaseValidator.__subclasses__():
        if cls.is_supported(fileinfo):
            found_validator = True
            validator = cls(fileinfo)
            yield validator

    for cls in JHoveBase.__subclasses__():
        if cls.is_supported(fileinfo):
            found_validator = True
            validator = cls(fileinfo)
            yield validator

    if not found_validator:
        validator = UnknownFileformat(fileinfo)
        yield validator
