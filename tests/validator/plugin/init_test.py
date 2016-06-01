"""
Test for ipt/validator/__init__.py. The purpose of this test is to make sure that all validators are able to be found.
"""
from ipt.validator.jhove import JHove, JHoveTextUTF8, JHovePDF, JHoveTiff, JHoveJPEG
from ipt.validator.dummytextvalidator import DummyTextValidator
from ipt.validator.xmllint import Xmllint
from ipt.validator.warctools import WarcTools
from ipt.validator.ghost_script import GhostScript
from ipt.validator.pngcheck import Pngcheck
from ipt.validator.csv_validator import PythonCsv
from ipt.validator import UnknownFileformat

import ipt.validator
import pytest


def test_iter_validator_classes():
    """
    test_iter_validator_classes
    """
    classes = [x for x in ipt.validator.iter_validator_classes()]
    assert set(classes) == set([JHove, JHoveTextUTF8, JHovePDF, JHoveTiff, JHoveJPEG, 
        DummyTextValidator, Xmllint, WarcTools, GhostScript, Pngcheck, PythonCsv])
    

@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["mimetype", "version", "charset", "validator_class"],
    [
        ("application/warc", "1.0", "", WarcTools),
        ("text/csv", "", "UTF-8", PythonCsv),
        ("text/plain", "", "ISO-8859-15", DummyTextValidator),
        ("video/mpeg", "1", "", UnknownFileformat),
        ("video/mpeg", "2", "", UnknownFileformat),
        ("video/mpeg", "4", "", UnknownFileformat),
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
        ("image/jp2", "", "", JHove),
        ("image/gif", "1987a", "", JHove),
        ("image/gif", "1989a", "", JHove),
        ("text/html", "HTML.4.01", "UTF-8", JHove),
        ("image/png", "", "", Pngcheck),
        ("application/warc", "0.17", "", WarcTools),
        ("application/warc", "0.18", "", WarcTools),
        ("application/warc", "1.0", "", WarcTools),
        ("application/x-internet-archive", "1.0", "", WarcTools),
        ("application/x-internet-archive", "1.1", "", WarcTools),
        ("text/xml", "1.0", "UTF-8", Xmllint)
    ])
def tests_validate_validator_found(monkeypatch, mimetype, version, charset, validator_class, capsys):
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
    print validator_class, ipt.validator.find_validator(fileinfo)
    assert isinstance(ipt.validator.find_validator(fileinfo), validator_class)

  