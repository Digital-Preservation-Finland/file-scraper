"""
Test for ipt/validator/__init__.py. The purpose of this test is to make sure that all validators are able to be found.
"""
from ipt.validator.jhove import JHoveBasic, JHoveTextUTF8, JHovePDF, \
    JHoveTiff, JHoveJPEG, JHoveHTML
from ipt.validator.dummytextvalidator import DummyTextValidator
from ipt.validator.xmllint import Xmllint
from ipt.validator.warctools import WarctoolsWARC, WarctoolsARC
from ipt.validator.ghost_script import GhostScript
from ipt.validator.pngcheck import Pngcheck
from ipt.validator.csv_validator import PythonCsv
from ipt.validator import UnknownFileformat, BaseValidator
from ipt.validator.ffmpeg import FFMpeg

import ipt.validator
import pytest
    

@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["mimetype", "version", "charset", "validator_class"],
    [
        ("application/warc", "1.0", "", WarctoolsWARC),
        ("text/csv", "", "UTF-8", PythonCsv),
        ("text/plain", "", "ISO-8859-15", DummyTextValidator),
        ("video/mpeg", "1", "", FFMpeg),
        ("video/mpeg", "2", "", FFMpeg),
        ("video/mp4", "", "", FFMpeg),
        ("application/pdf", "1.3", "", JHovePDF),
        ("application/pdf", "1.4", "", JHovePDF),
        ("application/pdf", "1.5", "", JHovePDF),
        ("application/pdf", "1.5", "", JHovePDF),
        ("application/pdf", "1.6", "", JHovePDF),
        ("application/pdf", "A-1a", "", JHovePDF),
        ("application/pdf", "A-1b", "", JHovePDF),
        ("application/pdf", "1.7", "", GhostScript),
        ("image/tiff", "6.0", "", JHoveTiff),
        ("image/jpeg", "", "", JHoveJPEG),
        ("image/jp2", "", "", JHoveBasic),
        ("image/gif", "1987a", "", JHoveBasic),
        ("image/gif", "1989a", "", JHoveBasic),
        ("text/html", "HTML.4.01", "UTF-8", JHoveHTML),
        ("image/png", "", "", Pngcheck),
        ("application/warc", "0.17", "", WarctoolsWARC),
        ("application/warc", "0.18", "", WarctoolsWARC),
        ("application/warc", "1.0", "", WarctoolsWARC),
        ("application/x-internet-archive", "1.0", "", WarctoolsARC),
        ("application/x-internet-archive", "1.1", "", WarctoolsARC),
        ("text/xml", "1.0", "UTF-8", Xmllint)
    ])
def tests_iter_validator_classes(mimetype, version, charset, validator_class):
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
    assert isinstance(
        ipt.validator.iter_validator_classes(fileinfo), validator_class)
