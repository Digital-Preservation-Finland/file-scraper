"""
Tests for main scraper.

This module tests that:
    - Monkeypatched is_textfile() returns True when scraper returns
      well-formed and False otherwise.
    - checksum() method returns correct checksums both using MD5 and SHA-1
      algorithms.
    - checksum() method raises ValueError when illegal algorithm is given.
    - checksum() method raises IOError when checksum calculation is attempted
      for a file that does not exist.
    - empty text files are not well-formed according to the scraper.
    - non-existent files are not well-formed according to the scraper.
    - giving None instead of a file name to the scraper results in successful
      scraping with a result of not well-formed.
    - file type detection without scraping works and respects the predefined
      file type if provided.
    - Character encoding detection works and respects the predefined file type
      if provided.
    - Grading works so that the correct digital preservation grade is returned.
    - Scraper works with undecodable filenames.
    - If a scraper has XML-incompatible characters in its messages or errors,
      they are filtered out correctly.
"""
import os
from pathlib import Path

import pytest
from dpres_file_formats.defaults import Grades
from dpres_file_formats.defaults import UnknownValue

from file_scraper.base import BaseMeta
from file_scraper.scraper import Scraper
from file_scraper.textfile.textfile_extractor import TextfileExtractor
from file_scraper.exceptions import (
    FileIsNotScrapable,
    FileNotFoundIsNotScrapable,
    DirectoryIsNotScrapable,
    InvalidMimetype,
    InvalidVersionForMimetype,
)

from tests.common import compare_results


def test_is_textfile():
    """Test that text files (and only text files) are identified as such."""
    textfiles = ["tests/data/text_plain/valid__ascii.txt",
                 "tests/data/text_plain/valid__iso8859.txt",
                 "tests/data/text_plain/valid__utf8_without_bom.txt"]
    binaryfiles = ["tests/data/text_plain/invalid__binary_data.txt",
                   "tests/data/image_png/valid_1.2.png",
                   "tests/data/application_pdf/valid_1.2.pdf"]
    for filename in textfiles:
        scraper = Scraper(filename)
        assert scraper.is_textfile()
    for filename in binaryfiles:
        scraper = Scraper(filename)
        assert scraper.is_textfile() is False


def test_checksum():
    """Test that checksum value of the file is returned."""
    scraper = Scraper("tests/data/text_plain/valid__utf8_without_bom.txt")
    assert scraper.checksum() == "b50b89c3fb5299713b7b272c1797a1e3"
    assert scraper.checksum("SHA-1") == \
        "92103972564bca86230dbfd311eec01f422cead7"
    with pytest.raises(ValueError):
        assert scraper.checksum("foo")


@pytest.mark.parametrize(
    (
        "filename",
        "params",
        "expected_mimetype",
        "expected_version",
    ),
    [
        # Valid file
        (
            "tests/data/application_pdf/valid_A-1a.pdf",
            {},
            "application/pdf",
            "A-1a",
        ),
        # Valid file using predefine mimetype
        (
            "tests/data/application_pdf/valid_A-1a.pdf",
            {"mimetype": "application/pdf"},
            "application/pdf",
            "A-1a",
        ),
        # Invalid file. Error not detected by detectors.
        (
            "tests/data/application_pdf/invalid_A-1a_payload_altered.pdf",
            {},
            "application/pdf",
            "A-1a",
        ),
        # File that is not detected correctly automatically. If version
        # can not be detected, the result should be `None`, not a wrong
        # version
        (
            "tests/data/image_png/valid_1.2.png",
            {},
            "image/png",
            None,
        ),
    ]
)
def test_detect_filetype(filename, params, expected_mimetype,
                         expected_version):
    """Test running only the filetype detection.

    This test ensures that the filetype detection detects correct
    mimetype and version. Streams should be empty. Detectors do not
    validate the file, so well_formed should be None or False, newer
    True. Info should also contain some entries, but their contents are
    not checked.

    :param filename: Test file name
    :param params: Parameters for Scarper
    :param expected_mimetype: Expected mimetype
    :param expected_version: Expected version
    :param well_formed: Should the file be well formed after detection
    """
    scraper = Scraper(filename, **params)
    mimetype, version = scraper.detect_filetype()
    assert mimetype == expected_mimetype
    assert version == expected_version
    assert not scraper.well_formed
    assert scraper.streams[0]["mimetype"] == expected_mimetype
    assert scraper.streams[0]["version"] == expected_version
    assert scraper.info

    # Detecting twice is not allowed
    with pytest.raises(RuntimeError, match="already detected"):
        scraper.detect_filetype()


@pytest.mark.parametrize(
    "charset",
    [None, "UTF-8", "ISO-8859-15"]
)
def test_charset_parameter(charset):
    """
    Test charset parameter.
    In the test we have an UTF-8 file. If given charset is None, it will be
    detected as UTF-8. Otherwise, the parameter value is used.

    :charset: Given character encoding
    """
    scraper = Scraper("tests/data/text_plain/valid__utf8_without_bom.txt",
                      charset=charset)
    scraper.detect_filetype()
    # pylint: disable=protected-access
    assert scraper._kwargs["charset"] in [charset, "UTF-8"]


@pytest.mark.parametrize(
    ("file_path", "expected_grade"),
    [
        # Recommended file format
        (
            "tests/data/text_plain/valid__ascii.txt",
            "fi-dpres-recommended-file-format"
        ),
        # Format version not accepted according to specification
        (
            "tests/data/application_warc/valid_0.17.warc",
            "fi-dpres-unacceptable-file-format"
        ),
        # Recommended container file format
        (
            "tests/data/video_x-matroska/valid_4_ffv1_flac.mkv",
            "fi-dpres-recommended-file-format"
        ),
        # Acceptable container file format due to containing acceptable audio
        # and video streams
        (
            "tests/data/video_MP2T/valid__mpeg2_mp3.ts",
            "fi-dpres-acceptable-file-format"
        ),
    ]
)
def test_grade(file_path, expected_grade):
    """Test that scraper returns correct digital preservation grade."""

    scraper = Scraper(file_path)

    # File can not be graded before scraping
    assert scraper.grade() == "(:unav)"

    # After scraping the file should have expected grade
    scraper.scrape()
    assert scraper.grade() == expected_grade


def test_undecodable_filename(tmpdir):
    """Test that scraper works with undecodable filenames.

    Creates a file with iso-8859-15 encoded name and tests that some
    methods work. All methods currently do not work, so they are not
    tested.
    """
    path = os.path.join(tmpdir, 'källi').encode('iso-8859-15')
    with open(path, 'w', encoding='utf-8') as file:
        file.write('foo')

    scraper = Scraper(path)
    # Nowadays ZipFile works with path-like objects
    # (https://docs.python.org/3/library/zipfile.html#zipfile-objects)
    # Note that all extractors should be tested with undecodable filenames.
    assert scraper.detect_filetype() == ("text/plain", None)
    scraper.scrape()
    assert scraper.grade() == "fi-dpres-recommended-file-format"
    assert scraper.is_textfile() is True
    assert scraper.checksum() == 'acbd18db4cc2f85cedef654fccc4a4d8'


def test_filter_unwanted_characters(monkeypatch):
    """Test that `utils.filter_unwanted_chars` replaces
    unwanted characters in `scraper.info` with an empty string"""

    # pylint: disable=protected-access
    def mock_scrape(self):
        self._messages.append("text\ntext null \x00\n")
        self._messages.append("short unicode \ufffe")
        self._errors.append("long unicode \U0005fffe")

    monkeypatch.setattr(TextfileExtractor, "extract", mock_scrape)

    scraper = Scraper("tests/data/text_plain/valid__ascii.txt")
    scraper.scrape()

    tfscraper = None
    for value in scraper.info.values():
        if value["class"] == "TextfileExtractor":
            tfscraper = value
            break

    assert tfscraper["messages"] == ["text\ntext null \n", "short unicode "]
    assert tfscraper["errors"] == ["long unicode "]


class MockBytePath:
    def __init__(self, path: bytes):
        self.path = path

    def __fspath__(self) -> bytes:
        return self.path


@pytest.mark.parametrize("path",
                         ["tests/data/audio_mpeg/invalid_contains_jpeg.mp3",
                          "tests/data/audio_mpeg/invalid_contains_png.mp3"])
def test_invalid_av_stream_combinations(path):
    """
    Test that files containing invalid stream combinations are rejected. In
    this the files are mp3 files with embedded images.
    """
    scraper = Scraper(path)
    scraper.scrape(check_wellformed=True)
    assert scraper.well_formed is not True
    assert len(scraper.streams) == 3
    assert scraper.grade() == Grades.UNACCEPTABLE


class TestPathValidation:
    @pytest.mark.parametrize(
            "pathlike",
            [
                "tests/data/text_plain/valid__ascii.txt",
                Path("tests/data/text_plain/valid__ascii.txt"),
                b"tests/data/text_plain/valid__ascii.txt",
                MockBytePath(b"tests/data/text_plain/valid__ascii.txt")
            ]
        )
    def test_different_pathlike_types(self, pathlike):
        scraper = Scraper(pathlike)
        scraper.scrape()
        assert scraper.well_formed

    @pytest.mark.parametrize("value", [None, 1, True, [], ()])
    def test_wrong_types(self, value):
        with pytest.raises(TypeError) as file_not_scrapable:
            Scraper(value)

        assert str(file_not_scrapable.value) == ("expected str, bytes or"
               " os.PathLike object, not %s" % value.__class__.__name__)

    @pytest.mark.parametrize(
        "path, error_message, error",
        [
            (
                "missing_file",
                "A file couldn't be found from the path: missing_file",
                FileNotFoundIsNotScrapable
            ),
            (
                "/dev/null",
                "The file is not a regular file and can't be scraped from"
                + " the path: /dev/null",
                FileIsNotScrapable
            ),
            (
                "/",
                "Instead of a file, a directory was found from the path: /",
                DirectoryIsNotScrapable
            )
        ]
    )
    def test_invalid_files(self, path, error_message, error):
        """Test invalid file input"""
        with pytest.raises(error) as err:
            Scraper(path)
        assert str(err.value) == error_message


@pytest.mark.parametrize(
    ["parameters", "error"],
    [
        ({"mimetype": UnknownValue.UNAL}, InvalidMimetype),
        (
            {"mimetype": "text/plain", "version": UnknownValue.UNAV},
            InvalidVersionForMimetype,
        ),
    ],
)
def test_invalid_unknown_parameters(parameters, error):
    with pytest.raises(error) as err:
        Scraper("tests/data/text_plain/valid__ascii.txt", **parameters)
    assert err.type is error


def test_only_version_input():
    """
    Version input without mimetype doesn't make sense, since version
    information can't be used without knowing the mimetype of the file.
    """
    with pytest.raises(InvalidMimetype) as err:
        Scraper("tests/data/text_plain/valid__ascii.txt", version="10")
    assert "Missing a mimetype parameter for the provided version 10" in str(
        err
    )


@pytest.mark.parametrize(
    ["filepath", "mimetype_parameter", "detected_mimetype"],
    [("tests/data/image_tiff/valid_6.0.tif",
      "application/pdf",
      "image/tiff"),
     ("tests/data/image_tiff/valid_6.0.tif",
      "audio/mpeg",
      "image/tiff"),
     ("tests/data/video_mp4/valid__h264_aac.mp4",
      "video/mpeg",
      "video/mp4"),]
)
def test_valid_but_invalid_combined_mimetype_input(
        filepath, mimetype_parameter, detected_mimetype):
    """
    A mimetype can be valid and the file can be valid, but the version input
    can be invalid.
    This can be found from the messages of the scraper output.
    """

    scraper = Scraper(filepath, mimetype=mimetype_parameter)
    scraper.scrape()
    assert ("User defined mimetype: '%s' not detected by "
            "detectors. Detectors detected a different mimetype: '%s'" % (
                mimetype_parameter, detected_mimetype) in str(scraper.info))


@pytest.mark.parametrize(
    "filepath, mimetype_parameter, version_parameter, error",
    [
        # Give the correct MIME type with unsupported version, resulting
        # user input error
        ("tests/data/image_tiff/valid_6.0.tif",
         "image/tiff", "99.9",
         "Given version 99.9 for the mimetype image/tiff is not supported"),

        # Give the correct MIME type, but wrong version
        ("tests/data/text_html/valid_4.01.html",
         "text/html", "0.0",
         "Given version 0.0 for the mimetype text/html is not supported"),
    ]
)
def test_invalid_version_mimetype_combinations(
        filepath, mimetype_parameter, version_parameter, error):
    """
    A mimetype can be valid and the file can be valid, but the version input
    can be invalid.
    This causes a value error with the correct type included in the error.
    """
    # Both Scraper and scrape function raise the ValueError
    with pytest.raises(InvalidVersionForMimetype) as val_err:
        scraper = Scraper(
            filepath,
            mimetype=mimetype_parameter,
            version=version_parameter
        )
        scraper.scrape()
    assert error in str(val_err)


def test_text_file_predefined_mimetype_correction():
    """Test detecting charset of special text files.

    Some text files are not automatically detected as text/plain by
    detectors. The mimetype must be predefined for these files, but
    charset should be detected correctly once the mimetype has been
    predefined. A webvtt file is used as an example in this test.
    """
    # Scraping without predefined mimetype does not produce valid result
    scraper = Scraper(
        "tests/data/text_plain/valid__webvtt.vtt",
    )
    scraper.scrape()
    assert scraper.mimetype == "text/vtt"
    assert scraper.streams[0].get("charset") is None
    assert scraper.well_formed is False

    # When mimetype is predefined, charset is detected and the file
    # well formed
    scraper = Scraper(
        "tests/data/text_plain/valid__webvtt.vtt",
        mimetype="text/plain"
    )
    scraper.scrape()
    assert scraper.mimetype == "text/plain"
    assert scraper.streams[0].get("charset") == "UTF-8"
    assert scraper.well_formed is True


@pytest.mark.parametrize(
    "path",
    [
        "text_plain/valid__ascii.txt",
        "video_mp4/invalid__h264_aac_missing_data.mp4",
        "audio_mpeg/invalid_contains_jpeg.mp3",
        "application_pdf/valid_1.3.pdf",
    ]
)
def test_scraper_returns_correct_values(path):
    """
    The scraper returns the same values which can be collected from
    the scraper object.
    """
    path = "tests/data/" + path

    scraper = Scraper(path)
    results = scraper.scrape()
    compare_results(scraper, results)

    scraper = Scraper(path)
    results = scraper.scrape(check_wellformed=False)
    compare_results(scraper, results)


def test_scraper_metadata_conflict():
    """Test handling conflicting metadata."""
    path = "tests/data/image_jpeg/valid_1.01.jpg"
    scraper = Scraper(path, mimetype="image/png")
    result = scraper.scrape()
    assert scraper.well_formed is False
    assert "The stream has conflicting mimetype image/jpeg" \
        in str(result.errors)
