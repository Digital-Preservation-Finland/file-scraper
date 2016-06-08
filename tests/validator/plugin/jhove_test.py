"""Test module for jhove.py"""
import os
import pytest

from ipt.validator.jhove import JHoveBasic, JHoveTiff, JHovePDF, \
    JHoveTextUTF8, JHoveJPEG

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version", "charset", "stdout"],
    [
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", None, None, "Well-Formed and valid"),
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", "1.01", None, "Well-Formed and valid"),
        (JHoveBasic, "02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.4.01", None, "Well-Formed and valid"),
        (JHovePDF, "test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
         "application/pdf", "1.4", None, "Well-Formed and valid"),
        (JHoveBasic, "02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "89a", None, "Well-Formed and valid"),
        (JHoveBasic, "02_filevalidation_data/gif_87a/valid.gif",
         "image/gif", "87a", None, "Well-Formed"),
        (JHovePDF, "02_filevalidation_data/pdfa-1/valid.pdf",
         "application/pdf", "1.4", None, "Well-Formed and valid"),
        (JHoveTiff, "02_filevalidation_data/tiff/valid.tif",
         "image/tiff", "6.0", None, "Well-Formed and valid"),
        (JHovePDF, "02_filevalidation_data/pdf_1_5/sample_1_5.pdf",
         "application/pdf", "1.5", None, "Well-Formed and valid"),
        (JHovePDF, "02_filevalidation_data/pdf_1_6/sample_1_6.pdf",
         "application/pdf", "1.6", None, "Well-Formed and valid"),
        (JHoveTiff, "02_filevalidation_data/tiff/valid_version5.tif",
         "image/tiff", "6.0", None, "Well-Formed and valid"),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.txt",
         "text/plain", None, "UTF-8", "Well-Formed and valid"),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.csv",
         "text/plain", None, "UTF-8", "Well-Formed and valid")
    ])
def test_validate_valid(validator_class, filename, mimetype, version, charset, stdout):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
        }
    }
    if charset:
        fileinfo["format"]["charset"] = charset
    if version:
        fileinfo["format"]["version"] = version

    validator = validator_class(fileinfo)
    validator.validate()
    assert validator.is_valid
    assert stdout in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version", "charset",
     "stdout"],
    [
        (JHoveBasic, "02_filevalidation_data/html/notvalid.htm",
         "text/html", "HTML.4.01", None, "Well-Formed, but not valid"),
        (JHoveBasic, "02_filevalidation_data/gif_89a/invalid.gif",
         "image/gif", "89a", None, "Not well-formed"),
        (JHoveBasic, "02_filevalidation_data/gif_87a/invalid.gif",
         "image/gif", "87a", None, "Not well-formed"),
        (JHovePDF, "02_filevalidation_data/pdfa-1/invalid.pdf",
         "application/pdf", "1.4", None, "Not well-formed"),
        (JHoveTiff, "02_filevalidation_data/tiff/invalid.tif",
         "image/tiff", "6.0", None, "Not well-formed")
    ])
def test_validate_invalid(validator_class, filename, mimetype, version,
                          charset, stdout):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
        }
    }
    if charset:
        fileinfo["format"]["charset"] = charset
    if version:
        fileinfo["format"]["version"] = version

    validator = validator_class(fileinfo)
    validator.validate()
    assert not validator.is_valid
    assert stdout in validator.messages()
    assert validator.errors() != ""
