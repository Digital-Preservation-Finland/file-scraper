"""Test for ipt/validator/__init__.py. The purpose of this test is to make sure
that all validators are able to be found."""

from ipt.validator.jhove import JHovePDF, \
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
from ipt.validator.vnu import Vnu
from ipt.validator.utils import UnknownFileformat

from ipt.validator.utils import iter_validators
import pytest


@pytest.mark.parametrize(
    ["mimetype", "version", "charset", "validator_classes"],
    [
        ("application/warc", "1.0", "", [WarctoolsWARC]),
        ("text/csv", "", "UTF-8", [PythonCsv]),
        ("text/plain", "", "ISO-8859-15", [DummyTextValidator]),
        ("text/plain", "", "UTF-8", [JHoveTextUTF8]),
        ("video/mpeg", "1", "", [FFMpeg]),
        ("video/mpeg", "2", "", [FFMpeg]),
        ("video/mp4", "", "", [FFMpeg]),
        ("application/pdf", "1.3", "", [JHovePDF]),
        ("application/pdf", "1.4", "", [JHovePDF]),
        ("application/pdf", "1.5", "", [JHovePDF]),
        ("application/pdf", "1.5", "", [JHovePDF]),
        ("application/pdf", "1.6", "", [JHovePDF]),
        ("application/pdf", "A-1a", "", [JHovePDF]),
        ("application/pdf", "A-1b", "", [JHovePDF]),
        ("application/pdf", "1.7", "", [GhostScript]),
        ("image/tiff", "6.0", "", [JHoveTiff, File, ImageMagick]),
        # JHoveJPEG accepts jpeg without version number
        ("image/jpeg", "", "", [JHoveJPEG]),
        ("image/jpeg", "1.00", "", [JHoveJPEG, File, ImageMagick]),
        ("image/jpeg", "1.01", "", [JHoveJPEG, File, ImageMagick]),
        ("image/jpeg", "1.02", "", [JHoveJPEG, File, ImageMagick]),
        ("image/gif", "1987a", "", [JHoveGif]),
        ("image/gif", "1989a", "", [JHoveGif]),
        ("text/html", "4.01", "UTF-8", [JHoveHTML]),
        ("text/html", "5.0", "UTF-8", [Vnu]),
        ("image/png", "", "", [Pngcheck, File, ImageMagick]),
        ("application/warc", "0.17", "", [WarctoolsWARC]),
        ("application/warc", "0.18", "", [WarctoolsWARC]),
        ("application/warc", "1.0", "", [WarctoolsWARC]),
        ("application/x-internet-archive", "1.0", "", [WarctoolsARC]),
        ("application/x-internet-archive", "1.1", "", [WarctoolsARC]),
        ("text/xml", "1.0", "UTF-8", [Xmllint]),
        ("text/unknown-mimetype", "1.0", "UTF-8", [UnknownFileformat]),
        # An erroneous mime type should return UnknownFileformat
        ("text/unknown-mimetype, text/unknown-mimetype", "1.0", "UTF-8",
         [UnknownFileformat]),
        ("application/vnd.oasis.opendocument.text", "1.0", "", [Office, File]),
        ("application/vnd.oasis.opendocument.text", "1.1", "", [Office, File]),
        ("application/vnd.oasis.opendocument.text", "1.2", "", [Office, File]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.0", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.1", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.2", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.presentation", "1.0", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.presentation", "1.1", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.presentation", "1.2", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.graphics", "1.0", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.graphics", "1.1", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.graphics", "1.2", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.formula", "1.0", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.formula", "1.1", "",
         [Office, File]),
        ("application/vnd.oasis.opendocument.formula", "1.2", "",
         [Office, File]),
        ("application/msword", "8.0", "", [Office, File]),
        ("application/msword", "8.5", "", [Office, File]),
        ("application/msword", "9.0", "", [Office, File]),
        ("application/msword", "10.0", "", [Office, File]),
        ("application/msword", "11.0", "", [Office, File]),
        ("application/vnd.ms-excel", "8.0", "", [Office, File]),
        ("application/vnd.ms-excel", "9.0", "", [Office, File]),
        ("application/vnd.ms-excel", "10.0", "", [Office, File]),
        ("application/vnd.ms-excel", "11.0", "", [Office, File]),
        ("application/vnd.ms-powerpoint", "8.0", "", [Office, File]),
        ("application/vnd.ms-powerpoint", "9.0", "", [Office, File]),
        ("application/vnd.ms-powerpoint", "10.0", "", [Office, File]),
        ("application/vnd.ms-powerpoint", "11.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "12.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "14.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "15.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "12.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "14.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "15.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "12.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "14.0", "", [Office, File]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "15.0", "", [Office, File]),
    ])
def tests_iter_validators(mimetype, version, charset, validator_classes):
    """
    Test for validator discovery.
    """
    fileinfo = {
        "filename": "foo",
        "format": {
            "mimetype": mimetype,
            "version": version,
            "charset": charset,
        },
        "addml": {
            "charset": charset,
            "separator": "foo",
            "delimiter": "foo",
            "header_fields": "foo"
        }
    }
    validators = iter_validators(fileinfo)
    assert set([type(x) for x in validators]) == set(validator_classes)
