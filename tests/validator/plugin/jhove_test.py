import os
import sys
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import pytest
#import testcommon.settings

from ipt.validator.plugin.jhove import Jhove

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))
TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))


@pytest.mark.parametrize(
    ["filename", "mimetype", "version", "exitcode", "stdout", "stderr"],
    [("gif_87a/wrong_mime.JPG", "image/gif", "", 117,
        "Invalid GIF header", "")])
def test_validate(filename, mimetype, version, exitcode, stdout, stderr):
    """Test cases of Jhove validation"""
    file_path = os.path.join(TESTDATADIR, filename)
    validator = Jhove(mimetype, version, file_path)
    (exitcode_result, stdout_result, stderr_result) = validator.validate()
    assert exitcode == exitcode_result
    assert stdout in stdout_result
    assert stderr in stderr_result


"""
def test_system_error():

    Test for system error(missing file)

    with pytest.raises(UnknownException):
        validator = WarcTools("application/warc", "1.0", "foo")
        validator.validate()

    with pytest.raises(WarcError):
        validator = WarcTools("foo", "1.0", "foo")
"""