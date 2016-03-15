"""
This is a test for ffmpeg.py.
"""
import os
import pytest

from ipt.validator.plugin.ffmpeg import FFMpeg

TEST_DATA_DIR_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data'))
TEST_DATA_PATH = os.path.abspath(
    os.path.join(TEST_DATA_DIR_BASE, '02_filevalidation_data', 'mpg'))


@pytest.mark.parametrize(
    ["filename", "stdout", "stderr", "exitcode"], [
        ("system_error", "", "", 1),
        ("hubble.mpg", "", "", 0),
        ("hubble_error.mpg", "", "Missing picture start code", 117)])
def test_mark_ffmpeg(filename, stdout, stderr, exitcode):
    """FFMpeg test."""
    file_path = os.path.join(TEST_DATA_PATH, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "version": "2",
            "mimetype": "video/mpeg"}
        }
    validator = FFMpeg(fileinfo=fileinfo)
    (result_exitcode, result_stdout, result_stderr) = validator.validate()

    assert stdout in result_stdout
    assert stderr in result_stderr
    assert exitcode == result_exitcode, result_exitcode
