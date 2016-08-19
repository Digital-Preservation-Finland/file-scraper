"""
This is a test for ffmpeg.py.
"""
import os
import pytest

from ipt.validator.ffmpeg import FFMpeg

TEST_DATA_DIR_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data'))
TEST_DATA_PATH = os.path.abspath(
    os.path.join(TEST_DATA_DIR_BASE, '02_filevalidation_data', 'mpg'))


@pytest.mark.parametrize(
    ["filename", "version", "stdout", "stderr", "exitcode"], [
        ("system_error", "1", "", "", 1),
        ("mpg1.mpg", "1", "", "", 0),
        ("mpg1_error.mpg", "1", "", "Missing picture start code", 117),
        ("mpg1_error2.mpg", "1", "", "", 117),
        ("mp4.mp4", "4", "", "", 0),
        ("mp4_error.mp4", "4", "", "Invalid data found", 117),
        ("mpg2.mpg", "2", "", "", 0),
        ("mpg2_error.mpg", "2", "", "", 117),
        ("mpg1.mpg", "4", "", "Wrong format version", 117),
        ("unknown_mimetype.3gp", "2", "", "Unknown mimetype or version", 117),
        ("no_video.wav", "1", "", "No version information could be found",
            117)])
def test_mark_ffmpeg(filename, version, stdout, stderr, exitcode):
    """FFMpeg test."""
    file_path = os.path.join(TEST_DATA_PATH, filename)
    fileinfo = {
        "filename": file_path,
        "format": {
            "version": version,
            "mimetype": "video/mpeg"}
        }
    validator = FFMpeg(fileinfo=fileinfo)
    (result_exitcode, result_stdout, result_stderr) = validator.validate()

    assert stdout in result_stdout
    assert stderr in result_stderr
    assert exitcode == result_exitcode
