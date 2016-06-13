"""Test module for jhove.py"""
import os
import pytest

from ipt.validator.jhove import JHoveBasic, JHoveTiff, JHovePDF, \
    JHoveTextUTF8, JHoveJPEG, JHoveHTML

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version"],
    [
        (JHoveHTML, "02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.4.01"),
        (JHovePDF, "test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
         "application/pdf", "1.4"),
        (JHoveBasic, "02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "89a"),
        (JHoveBasic, "02_filevalidation_data/gif_87a/valid.gif",
         "image/gif", "87a"),
        (JHoveTiff, "02_filevalidation_data/tiff/valid.tif",
         "image/tiff", "6.0"),
        (JHovePDF, "02_filevalidation_data/pdf_1_5/sample_1_5.pdf",
         "application/pdf", "1.5"),
        (JHovePDF, "02_filevalidation_data/pdf_1_6/sample_1_6.pdf",
         "application/pdf", "1.6"),
        (JHoveTiff, "02_filevalidation_data/tiff/valid_version5.tif",
         "image/tiff", "6.0"),
        (JHoveHTML, "02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.4.01"),
    ])
def test_validate_valid_form_and_version(
        validator_class, filename, mimetype, version):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = validator_class(fileinfo)
    validator.validate()
    assert validator.is_valid
    assert "Well-Formed and valid" in validator.messages()
    assert "Version check OK" in validator.messages()
    assert "Profile check OK" not in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version", "charset"],
    [
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", None, None),
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", "1.01", None),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.txt",
         "text/plain", None, "UTF-8"),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.csv",
         "text/plain", None, "UTF-8"),
    ])
def test_validate_valid_only_form(validator_class, filename, mimetype, version,
                                  charset):
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
    assert "Well-Formed and valid" in validator.messages()
    assert "Version check OK" not in validator.messages()
    assert "Profile check OK" not in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version",
     "stdout"],
    [
        (JHoveHTML, "02_filevalidation_data/html/notvalid.htm",
         "text/html", "HTML.4.01", "Well-Formed, but not valid"),
        (JHoveBasic, "02_filevalidation_data/gif_89a/invalid.gif",
         "image/gif", "89a", "Not well-formed"),
        (JHoveBasic, "02_filevalidation_data/gif_87a/invalid.gif",
         "image/gif", "87a", "Not well-formed"),
        (JHovePDF, "02_filevalidation_data/pdfa-1/invalid.pdf",
         "application/pdf", "1.4", "Not well-formed"),
        (JHoveTiff, "02_filevalidation_data/tiff/invalid.tif",
         "image/tiff", "6.0", "Not well-formed"),
        (JHovePDF, "test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
         "application/pdf", "A-1a", ""),
    ])
def test_validate_invalid(validator_class, filename, mimetype, version,
                          stdout):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = validator_class(fileinfo)
    validator.validate()
    assert not validator.is_valid, validator.messages() + validator.errors()
    assert stdout in validator.messages()
    assert validator.errors() != ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version"],
    [
        (JHoveBasic, "02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "87a"),
        (JHoveHTML, "02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.3.2"),
    ])
def test_validate_version_error(validator_class, filename, mimetype, version):
    """
    test_validate_version_error
    """
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }
    validator = validator_class(fileinfo)
    validator.validate()
    assert not validator.is_valid
    assert "ERROR: File version is" in validator.errors()


def test_utf8_supported():
    """
    test_utf8_supported
    """
    fileinfo = {
        "filename": "foo",
        "format": {
            "mimetype": "text/plain",
            "charset": "UTF-8"
        }
    }
    validator = JHoveTextUTF8(fileinfo)
    assert validator.is_supported_mimetype(fileinfo)

    fileinfo["format"]["charset"] = "foo"
    validator = JHoveTextUTF8(fileinfo)
    assert not validator.is_supported_mimetype(fileinfo)


def test_pdf_profile():
    """
    test_pdf_profile
    """
    file_path = os.path.join(
        TESTDATADIR_BASE, "02_filevalidation_data/pdfa-1/valid.pdf")
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": "application/pdf",
            "version": "A-1a"
        }
    }
    validator = JHovePDF(fileinfo)
    validator.validate()
    assert validator.is_valid, validator.messages() + validator.errors()
    for text in [
            "Well-Formed and valid", "Version check OK", "Profile check OK"]:
        assert text in validator.messages()
    assert validator.errors() == ""
