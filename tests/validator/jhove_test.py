"""Test module for jhove.py"""
import os
import pytest

from ipt.validator.jhove import JHoveGif, JHoveTiff, JHovePDF, \
    JHoveTextUTF8, JHoveJPEG, JHoveHTML, JHoveWAV

TESTDATADIR_BASE = 'tests/data'


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version", "charset"],
    [
        (JHoveHTML, "02_filevalidation_data/html/valid.htm",
         "text/html", "4.01", "UTF-8"),
        (JHoveGif, "02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "1989a", ""),
        (JHoveGif, "02_filevalidation_data/gif_87a/valid.gif",
         "image/gif", "1987a", ""),
        (JHoveTiff, "02_filevalidation_data/tiff/valid.tif",
         "image/tiff", "6.0", ""),
        (JHovePDF, "02_filevalidation_data/pdf_1_4/sample_1_4.pdf",
         "application/pdf", "1.4", ""),
        (JHovePDF, "02_filevalidation_data/pdf_1_5/sample_1_5.pdf",
         "application/pdf", "1.5", ""),
        (JHovePDF, "02_filevalidation_data/pdf_1_6/sample_1_6.pdf",
         "application/pdf", "1.6", ""),
        (JHovePDF, "02_filevalidation_data/pdfa-2/pdfa2-pass-a.pdf",
         "application/pdf", "1.4", ""),
        (JHovePDF, "02_filevalidation_data/pdfa-3/pdfa3-pass-a.pdf",
         "application/pdf", "1.7", ""),
        (JHovePDF, "02_filevalidation_data/pdfa-1/valid.pdf",
         "application/pdf", "1.4", ""),
        (JHovePDF, "02_filevalidation_data/pdfa-2/pdfa2-fail-a.pdf",
         "application/pdf", "1.7", ""),
        (JHovePDF, "02_filevalidation_data/pdfa-3/pdfa3-fail-a.pdf",
         "application/pdf", "1.7", ""),
        (JHoveTiff, "02_filevalidation_data/tiff/valid_version5.tif",
         "image/tiff", "6.0", ""),
        (JHoveHTML, "02_filevalidation_data/xhtml/minimal_valid_sample.xhtml",
         "application/xhtml+xml", "1.0", "UTF-8"),
        (JHoveWAV, "02_filevalidation_data/wav/valid-wav.wav",
         "audio/x-wav", "", ""),
        (JHoveWAV, "02_filevalidation_data/wav/valid-bwf.wav",
         "audio/x-wav", "2", "")
    ])
def test_validate_valid_form_and_version(
        validator_class, filename, mimetype, version, charset):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    metadata_info = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }
    # Add charset to test KDKPAS-1589 and TPAS-66
    # If the charset is specified in mets.xml, it will be in
    # metadata_info["format"]
    if charset:
        metadata_info["format"]["charset"] = charset

    validator = validator_class(metadata_info)
    validator.validate()
    assert validator.is_valid, validator.errors()
    assert "Well-Formed and valid" in validator.messages()
    assert "Validation version check OK" in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version", "charset"],
    [
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", "1.01", None),
        (JHoveJPEG, "test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", "1.01", None),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.txt",
         "text/plain", None, "UTF-8"),
        (JHoveTextUTF8, "02_filevalidation_data/text/utf8.csv",
         "text/plain", None, "UTF-8"),
        (JHoveTextUTF8, "02_filevalidation_data/html/valid.htm",
         "text/html", "4.01", "UTF-8")
    ])
def test_validate_valid_only_form(validator_class, filename, mimetype, version,
                                  charset):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    metadata_info = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
        }
    }
    if charset:
        metadata_info["format"]["charset"] = charset
    if version:
        metadata_info["format"]["version"] = version

    validator = validator_class(metadata_info)
    validator.validate()
    assert validator.is_valid, validator.errors()
    assert "Well-Formed and valid" in validator.messages()
    assert "OK" in validator.messages()
    assert validator.errors() == ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version",
     "stdout"],
    [
        (JHoveHTML, "02_filevalidation_data/html/notvalid.htm",
         "text/html", "HTML.4.01", "Well-Formed, but not valid"),
        (JHoveGif, "02_filevalidation_data/gif_89a/invalid.gif",
         "image/gif", "89a", "Not well-formed"),
        (JHoveGif, "02_filevalidation_data/gif_87a/invalid.gif",
         "image/gif", "87a", "Not well-formed"),
        (JHovePDF, "02_filevalidation_data/pdfa-1/invalid.pdf",
         "application/pdf", "1.4", "Not well-formed"),
        (JHoveTiff, "02_filevalidation_data/tiff/invalid.tif",
         "image/tiff", "6.0", "Not well-formed"),
        (JHovePDF, "test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
         "application/pdf", "A-1a", ""),
        (JHoveTextUTF8, "02_filevalidation_data/text/iso-8859.txt",
         "text/plain", "", "Not well-formed"),
        (JHoveWAV,
         "02_filevalidation_data/wav/invalid-wav-last-byte-missing.wav",
         "audio/x-wav", "", "Not well-formed"),
    ])
def test_validate_invalid(validator_class, filename, mimetype, version,
                          stdout):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    metadata_info = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }

    validator = validator_class(metadata_info)
    validator.validate()
    assert not validator.is_valid, validator.messages() + validator.errors()
    assert stdout in validator.messages()
    assert validator.errors() != ""


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["validator_class", "filename", "mimetype", "version"],
    [
        (JHoveGif, "02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "87a"),
        (JHoveHTML, "02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.3.2"),
    ])
def test_validate_version_error(validator_class, filename, mimetype, version):
    """
    test_validate_version_error
    """
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    metadata_info = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }
    validator = validator_class(metadata_info)
    validator.validate()
    assert not validator.is_valid
    assert 'ERROR: Metadata mismatch: found version "' in validator.errors()


@pytest.mark.usefixtures("monkeypatch_Popen")
def test_ignore_alt_format_in_mimetype():
    """
    Test that optional parameter 'alt-format' in format is ignored

    Related to KDKPAS-1545
    """
    metadata_info = {
        "filename": os.path.join(
            TESTDATADIR_BASE, "02_filevalidation_data/html/valid.htm"),
        "format": {
            "mimetype": "text/html",
            "alt-format": "text/hypothetical-text-markup-language",
            "version": "4.01"
        }
    }
    validator = JHoveHTML(metadata_info)
    validator.validate()
    print validator.errors()
    assert validator.is_valid, validator.errors()
    assert validator.errors() == ""


def test_utf8_supported():
    """
    test_utf8_supported
    """
    metadata_info = {
        "filename": "foo",
        "format": {
            "mimetype": "text/plain",
            "version": "",
            "charset": "UTF-8"
        }
    }
    validator = JHoveTextUTF8(metadata_info)
    assert validator.is_supported(metadata_info)

    metadata_info["format"]["charset"] = "foo"
    validator = JHoveTextUTF8(metadata_info)
    assert not validator.is_supported(metadata_info)


def test_audiomd_metadata():
    """Test the audiomd metadata validation"""
    metadata_info = {
        "filename": "tests/data/02_filevalidation_data/wav/valid-wav.wav",
        "format": {
            "mimetype": "audio/x-wav",
            "version": ""
        },
        "channels": "1",
        "sample_rate": "48",
        "bits_per_sample": "16"
    }

    validator = JHoveWAV(metadata_info)
    validator.validate()
    assert validator.is_valid, validator.errors()
    assert "Well-Formed and valid" in validator.messages()
    assert "Validation version check OK" in validator.messages()
    assert "Validation audio metadata check OK" in validator.messages()
    assert validator.errors() == ""


def test_audiomd_metadata_fail():
    """Test the audiomd metadata validation with invalid metadata."""
    metadata_info = {
        "filename": "tests/data/02_filevalidation_data/wav/valid-wav.wav",
        "format": {
            "mimetype": "audio/x-wav",
            "version": ""
        },
        "channels": "2",
        "sample_rate": "48",
        "bits_per_sample": "8"
    }

    validator = JHoveWAV(metadata_info)
    validator.validate()
    assert not validator.is_valid, validator.messages() + validator.errors()
    assert "Metadata mismatch: found channels" in validator.errors()
    assert "Metadata mismatch: found bits_per_sample" in validator.errors()
    assert validator.errors() != ""
