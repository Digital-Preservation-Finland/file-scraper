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

from file_scraper.scraper import Scraper
from file_scraper.textfile.textfile_extractor import TextfileExtractor
from file_scraper.exceptions import FileIsNotScrapable


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
    ["filename", "params", "expected_results"],
    [
        ("tests/data/image_png/valid_1.2.png", {},
         {"_detected_mimetype": "image/png", "_detected_version": "1.0",
          "well_formed": None}),
        ("tests/data/image_png/invalid_1.2_wrong_CRC.png", {},
         {"_detected_mimetype": "image/png", "_detected_version": "1.0",
          "well_formed": None}),
        ("tests/data/application_pdf/valid_A-1a.pdf",
         {"mimetype": "application/pdf"},
         {"_detected_mimetype": "application/pdf",
          "_detected_version": "A-1a", "well_formed": None}),
    ]
)
def test_detect_filetype(filename, params, expected_results):
    """
    Test running only the filetype detection.

    This test ensures that the filetype detection fills in mimetype and version
    (if available from detectors) for the file, leaving well_formed and
    streams as None. Info should also contain some entries, but their contents
    are not checked.

    Then it is tested that the same results are also returned if full scraping
    is run before filetype detection.

    :filename: Test file name
    :params: Parameters for Scarper
    :expected_results: Expected results, containing expected values of Scraper
                       attributes
    """
    # Filetype detection should work without scraping
    # change it later to skip initial path validation
    scraper = Scraper(filename, **params)
    scraper.detect_filetype()
    for field, value in expected_results.items():
        assert getattr(scraper, field) == value
    assert scraper.streams is None
    assert scraper.info

    # Even if scraping has been done previously, detection should erase all
    # streams and other information, except arguments given to scraper
    scraper.scrape()
    scraper.detect_filetype()
    for field, value in expected_results.items():
        assert getattr(scraper, field) == value
    assert scraper.streams is None
    assert scraper.info


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
                FileNotFoundError
            ),
            (
                "/dev/null",
                "The file is not a regular file and can't be scraped from"
                + " the path: /dev/null",
                FileIsNotScrapable
            )
        ]
    )
    def test_invalid_files(self, path, error_message, error):
        """Test invalid file input"""
        with pytest.raises(error) as err:
            Scraper(path)
        assert str(err.value) == error_message


@pytest.mark.parametrize(('meta_classes', 'wellformed'), [
    (['meta1', 'meta5'], None),
    (['meta1', 'meta2'], False)
])
def test_results_merging(meta_class_fx, meta_classes, wellformed):
    """Test that scraper merges extractor results properly. The test tests
    both a successful case where metadata could be merged and a case with
    conflicts in metadata resulting in the well-formedness being false. Also
    in the conflicting case, tool errors are checked to contain a
    descriptive error.
    """
    filename = Path("tests/data/text_plain/valid__ascii.txt")
    results = []
    for meta_class in meta_classes:
        results.append([meta_class_fx(meta_class)])

    scraper = Scraper(filename)
    scraper._kwargs["extractor_results"] = results
    scraper.info = {}
    scraper.check_wellformed = True
    scraper._merge_results()
    assert scraper.well_formed == wellformed
    if wellformed is False:
        assert list(filter((lambda s: "Conflict with values" in s),
                           scraper.info[0]["errors"]))


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
def test_invalid_mimetype_input(
        filepath, mimetype_parameter, detected_mimetype):
    """
    A mimetype can be valid and the file can be valid, but the version input
    can be invalid.
    This causes a value error with the correct type included in the error.
    """
    with pytest.raises(ValueError) as val_err:
        scraper = Scraper(filepath,
                          mimetype=mimetype_parameter)
        scraper.scrape()
    assert ("User defined mimetype: '%s' not detected by "
            "detectors. Detectors detected a different mimetype: '%s'" % (
                mimetype_parameter, detected_mimetype) in str(val_err))


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
    with pytest.raises(ValueError) as val_err:
        scraper = Scraper(
            filepath,
            mimetype=mimetype_parameter,
            version=version_parameter
        )
        scraper.scrape()
    assert error in str(val_err)
