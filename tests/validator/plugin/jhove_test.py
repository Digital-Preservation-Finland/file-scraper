"""Test module for jhove.py"""
import os
import pytest

from ipt.validator.jhove import JHove, JHoveTiff, JHovePDF, JHoveTextUTF8

TESTDATADIR_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data'))
TESTDATADIR = os.path.abspath(
    os.path.join(TESTDATADIR_BASE, '02_filevalidation_data'))


@pytest.mark.usefixtures("monkeypatch_Popen")
@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "exitcode", "stdout", "stderr"],
    [
        ("test-sips/CSC_test001/kuvat/P1020137.JPG",
         "image/jpeg", "", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/html/valid.htm",
         "text/html", "HTML.4.01", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/html/notvalid.htm",
         "text/html", "HTML.4.01", False, "Well-Formed, but not valid", ""),
        ("test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
         "application/pdf", "1.4", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/gif_89a/valid.gif",
         "image/gif", "89a", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/gif_89a/invalid.gif",
         "image/gif", "89a", False, "Not well-formed", ""),
        ("02_filevalidation_data/gif_87a/valid.gif",
         "image/gif", "87a", True, "Well-Formed", ""),
        ("02_filevalidation_data/gif_87a/invalid.gif",
         "image/gif", "87a", False, "Not well-formed", ""),
        ("02_filevalidation_data/pdfa-1/valid.pdf",
         "application/pdf", "1.4", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/pdfa-1/invalid.pdf",
         "application/pdf", "1.4", False, "Not well-formed", ""),
        ("02_filevalidation_data/tiff/valid.tif",
         "image/tiff", "6.0", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/tiff/invalid.tif",
         "image/tiff", "6.0", False, "Not well-formed", ""),
        ("02_filevalidation_data/pdf_1_5/sample_1_5.pdf",
         "application/pdf", "1.5", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/pdf_1_6/sample_1_6.pdf",
         "application/pdf", "1.6", True, "Well-Formed and valid", ""),
        ("02_filevalidation_data/tiff/valid_version5.tif",
         "image/tiff", "6.0", 0, "Well-Formed and valid", ""),
        ("02_filevalidation_data/text/utf8.txt",
         "text/plain", "UTF-8", 0, "Well-Formed and valid", ""),
        ("02_filevalidation_data/text/utf8.csv",
         "text/plain", "UTF-8", 0, "Well-Formed and valid", ""),
    ])
def test_validate(filename, mimetype, version, exitcode, stdout, stderr, capsys):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "mimetype": mimetype,
            "version": version
        }
    }
    if mimetype == 'image/tiff':
        validator = JHoveTiff(fileinfo)
    elif mimetype == 'application/pdf':
        validator = JHovePDF(fileinfo)
    elif mimetype == 'text/plain':
        validator = JHoveTextUTF8(fileinfo)
    else:
        validator = JHove(fileinfo)
    print capsys.readouterr()
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode == exitcode_result
    assert stdout in stdout_result
    assert stderr in stderr_result


@pytest.mark.usefixtures("monkeypatch_Popen")
def test_system_error(monkeypatch):
    """
    Test for system error(missing file)
    """

    # jhove command not found
    with pytest.raises(OSError):
        file_path = os.path.join(TESTDATADIR, "gif_87a/valid.gif")
        fileinfo = {
            "filename": file_path,
            "format": {
                "mimetype": "image/gif",
                "version": "1.0"
            }
        }

        validator = JHove(fileinfo)
        monkeypatch.setattr(validator, 'exec_cmd', ['foo'])
        validator.validate()
