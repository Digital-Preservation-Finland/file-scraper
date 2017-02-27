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
from ipt.validator.utils import UnknownFileformat

from ipt.validator.utils import iter_validators
import pytest


@pytest.mark.parametrize(
    ["mimetype", "version", "charset", "validator_classes"],
    [
        ("application/warc", "1.0", "", [WarctoolsWARC]),
        ("text/csv", "", "UTF-8", [PythonCsv]),
        ("text/plain", "", "ISO-8859-15", [DummyTextValidator, JHoveTextUTF8]),
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
        ("image/tiff", "6.0", "", [JHoveTiff]),
        ("image/jpeg", "", "", [JHoveJPEG]),
        ("image/gif", "1987a", "", [JHoveGif]),
        ("image/gif", "1989a", "", [JHoveGif]),
        ("text/html", "HTML.4.01", "UTF-8", [JHoveHTML]),
        ("image/png", "", "", [Pngcheck]),
        ("application/warc", "0.17", "", [WarctoolsWARC]),
        ("application/warc", "0.18", "", [WarctoolsWARC]),
        ("application/warc", "1.0", "", [WarctoolsWARC]),
        ("application/x-internet-archive", "1.0", "", [WarctoolsARC]),
        ("application/x-internet-archive", "1.1", "", [WarctoolsARC]),
        ("text/xml", "1.0", "UTF-8", [Xmllint]),
        ("text/unknown-mimetype", "1.0", "UTF-8", [UnknownFileformat])
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
    assert [type(x) for x in validators] == validator_classes
