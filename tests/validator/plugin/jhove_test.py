import os
import sys
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import pytest
#import testcommon.settings

from ipt.validator.plugin.jhove import Jhove
from ipt.utils import UnknownException, ValidationException

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))
TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "exitcode", "stdout", "stderr"],
    [
    ("02_filevalidation_data/gif_87a/wrong_mime.JPG",
        "image/gif", "", 117, "Invalid GIF header", ""),
    ("test-sips/CSC_test001/kuvat/P1020137.JPG",
        "image/jpeg", "", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/html/valid.htm",
        "text/html", "HTML.4.01", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/html/notvalid.htm",
        "text/html", "HTML.4.01", 117, "Well-Formed, but not valid", ""),
    ("test-sips/CSC_test004/fd2009-00002919-pdf001.pdf",
        "application/pdf", "1.4", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/gif_89a/valid.gif",
        "image/gif", "89a", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/gif_89a/invalid.gif",
        "image/gif", "89a", 117, "Not well-formed", ""),
    ("02_filevalidation_data/gif_87a/valid.gif",
        "image/gif", "87a", 0, "Well-Formed", ""),
    ("02_filevalidation_data/gif_87a/invalid.gif",
        "image/gif", "87a", 117, "Not well-formed", ""),
    ("02_filevalidation_data/pdfa-1/valid.pdf",
        "application/pdf", "1.4", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/pdfa-1/invalid.pdf",
        "application/pdf", "1.4", 117, "Not well-formed", ""),
    ("02_filevalidation_data/tiff/valid.tif",
        "image/tiff", "6.0", 0, "Well-Formed and valid", ""),
    ("02_filevalidation_data/tiff/invalid.tif",
        "image/tiff", "6.0", 117, "Not well-formed", ""),
    ])
def test_validate(filename, mimetype, version, exitcode, stdout, stderr):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR_BASE, filename)
    validator = Jhove(mimetype, version, file_path)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode == exitcode_result
    assert stdout in stdout_result
    assert stderr in stderr_result


def test_system_error(monkeypatch):
    """
    Test for system error(missing file)
    """

    # Jhove module not found for mimetype
    with pytest.raises(ValidationException):
        file_path = os.path.join(TESTDATADIR, "gif_87a/valid.gif")
        Jhove("foo", "1.0", file_path)

    # jhove command not found
    with pytest.raises(OSError):
        file_path = os.path.join(TESTDATADIR, "gif_87a/valid.gif")
        validator = Jhove("image/gif", "1.0", file_path)
        monkeypatch.setattr(validator, 'exec_cmd', ['foo'])
        validator.validate()

