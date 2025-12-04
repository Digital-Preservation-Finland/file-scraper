"""
Tests for utils.py

This module tests that the following utility functions fulfil the following
requirements:
    - hexdigest
        - Returns the hash of the given file, both for text and binary data.
        - Defaults to SHA-1 algorithm for calculating the hash.
        - MD5 algorithm can also be used.
        - An extra hash can be given to the function and this extra hash is
          appended to the file in calculation
    - iso8601_duration
        - Seconds are rounded to two decimal places according to normal rules.
        - If decimal places are not needed, they are not printed, i.e. 1 s
          converts to "PT1S" and 0.1 s to "PT0.1S".
        - If 60 s or a number that is rounded to 60 s is given, "PT1M" is
          printed.
        - If a duration greater than 60 s is given, minutes and seconds are
          printed separately, e.g. "PT1M1S", with approppriate decimal places
          in the seconds.
        - The following full 60 seconds (or seconds that are rounded to 60)
          increase the minutes. 0S is not printed when there are full minutes.
        - Time can increase to "PT59M59.99S" without hours being returned.
        - When seconds are rounded to 3600 s, "PT1H" is returned.
        - When full hours are present, minutes and seconds are part of the
          returned string only when there is a non-zero number of them.
        - Times exceeding 24 hours are not converted to days.
    - concat
        - Concatenation of empty list with or without a prefix produces an
          empty string.
        - Concatenation of a single string list produces the same string.
        - Concatenation of two item list produces a single string containing
          the items separated by a newline.
        - Concatenation of a single string list while using a prefix produces
          a single string containing the prefix followed by the list item.
        - Concatenation of a two item list while using a prefix produces
          a single string containing each of the items prefixed with the
          prefix, and the two separated by a newline.
    - iter_utf_bytes
        - UTF iterator works as designed with different files and encodings
    - iter_utf_bytes_trivial
        - UTF iterator works as designed if there is only UTF control
          character (c3) in a file
"""

import zipfile
from pathlib import Path

import pytest

from file_scraper.utils import (
    concat,
    hexdigest,
    is_zipfile,
    iso8601_duration,
    iter_utf_bytes,
    normalize_charset,
    strip_zeros,
    parse_exif_version
)


@pytest.mark.parametrize(
    ["filepath", "extra_hash", "algorithm", "expected_hash"],
    [
        ("tests/data/text_plain/valid__utf8_without_bom.txt", None, None,
         "92103972564bca86230dbfd311eec01f422cead7"),
        ("tests/data/image_png/valid_1.2.png", None, "SHA-1",
         "a7947ca260c313a4e7ece2312fd25db6cbcb9283"),
        ("tests/data/text_plain/valid__utf8_without_bom.txt", b"abc123", None,
         "b047b952ae6c97060ff479661e8133654f8a3095"),
        ("tests/data/image_png/valid_1.2.png", None, "MD5",
         "ce778faab1d293275a471df03faecdcd")
    ]
)
def test_hexdigest(filepath, extra_hash, algorithm, expected_hash):
    """
    Test that hexdigest returns correct sha1 and MD5 hashes.

    :filepath: Test file name
    :extra_hash: Hash of depending file(s), or None if no such dependency
    :algorithm: Hash algorithm
    :expected_hash: Expected hash result
    """
    if algorithm is None:
        assert hexdigest(filepath, extra_hash=extra_hash) == expected_hash
    else:
        assert hexdigest(filepath, algorithm=algorithm,
                         extra_hash=extra_hash) == expected_hash


@pytest.mark.parametrize(
    ["charset", "norm_charset"],
    [
        ("utf-8", "UTF-8"),         # Converted to upper-case
        ("US-ASCII", "UTF-8"),      # UTF-8 backwards compatible w/ ASCII
        ("ISO-8859-1", "ISO-8859-15"),  # Identical except for 8 characters

        ("UTF-16LE", "UTF-16"),  # Endianness is ignored
        ("UTF-16BE", "UTF-16")
    ]
)
def test_normalize_charset(charset, norm_charset):
    """
    Test that 'normalize_charset' converts a charset name to its most common
    and supported form
    """
    assert normalize_charset(charset) == norm_charset


@pytest.mark.parametrize(
    ["seconds", "expected_output"],
    [
        (0, "PT0S"),
        (0.001, "PT0S"),
        (0.004999999, "PT0S"),
        (0.005, "PT0.01S"),
        (0.01, "PT0.01S"),
        (0.1, "PT0.1S"),
        (1, "PT1S"),
        (59.99, "PT59.99S"),
        (59.999, "PT1M"),
        (60, "PT1M"),
        (61, "PT1M1S"),
        (119.99, "PT1M59.99S"),
        (119.999, "PT2M"),
        (3599, "PT59M59S"),
        (3599.99, "PT59M59.99S"),
        (3599.999, "PT1H"),
        (3600, "PT1H"),
        (3600.001, "PT1H"),
        (3601, "PT1H1S"),
        (3660, "PT1H1M"),
        (7199.999, "PT2H"),
        (7245.5, "PT2H45.5S"),
        (1234567.89, "PT342H56M7.89S")
    ]
)
def test_iso8601_duration(seconds, expected_output):
    """Test that duration in seconds is converted to "PT[hh]H[mm]M[ss.ss]S".

    If some parts are not present, e.g. there are no full hours or decimal
    parts in seconds, it is checked that those parts are not present in the
    returned string, with the exception that for a zero-duration time PT0S is
    returned.

    :seconds: Seconds to be converted
    :expected_output: ISO8601 representation of seconds
    """
    assert iso8601_duration(seconds) == expected_output


@pytest.mark.parametrize(
    ["float_str", "expected_output"],
    [
        ("123.456", "123.456"),
        ("123.4560", "123.456"),
        ("123.456000", "123.456"),
        ("123.0456", "123.0456"),
        ("123.000", "123"),
        ("123.0", "123"),
        ("450.0", "450"),
        ("450", "450"),
        ("0123.0", "0123"),
        ("1000000", "1000000"),
        ("1_000_000", "1_000_000"),
        ("1_234_000.0", "1_234_000"),
        ("1_234_000.000_000", "1_234_000")
    ]
)
def test_strip_zeros(float_str, expected_output):
    """
    Test stripping decimal zeros from string representation of a float.

    :float_str: Float string
    :expected_output: Float string where decimal zeros are stripped
    """

    assert strip_zeros(float_str) == expected_output


def test_concat():
    """Test concat function."""
    assert concat([]) == ""
    assert concat(["test"]) == "test"
    assert concat(["test1", "test2"]) == "test1\ntest2"
    assert concat([], "prefix:") == ""
    assert concat(["test"], "prefix:") == "prefix:test"
    assert (concat(["test1", "test2"], "prefix:") ==
            "prefix:test1\nprefix:test2")


@pytest.mark.parametrize(
    "filename, charset", [
        ("valid__utf8_without_bom.txt", "UTF-8"),
        ("valid__utf8_bom.txt", "UTF-8"),
        ("valid__utf16le_without_bom.txt", "UTF-16"),
        ("valid__utf16le_bom.txt", "UTF-16"),
        ("valid__utf16be_without_bom.txt", "UTF-16"),
        ("valid__utf16be_bom.txt", "UTF-16"),
        ("valid__utf16be_multibyte.txt", "UTF-16"),
        ("valid__utf16le_multibyte.txt", "UTF-16"),
        ("valid__utf8_multibyte.txt", "UTF-8"),
        ]
)
def test_iter_utf_bytes(filename, charset):
    """
    Test utf iterator.

    :filename: Test file name
    :charset: Character encoding
    """
    with open("tests/data/text_plain/" + filename, "rb") as infile:
        original_bytes = infile.read()
        original_text = original_bytes.decode(charset)
        for chunksize in range(4, 40):
            infile.seek(0)
            chunks = b""
            for chunk in iter_utf_bytes(infile, chunksize, charset):
                assert chunk.decode(charset)
                chunks += chunk
            assert chunks.decode(charset)
            assert original_text == chunks.decode(charset)
            assert original_bytes == chunks


def test_iter_utf_bytes_trivial():
    """
    Test that the iterator ends also in trivial case.
    The test file contains just 0xc3 which can not be decoded.
    """
    with open("tests/data/text_plain/invalid__utf8_just_c3.txt",
              "rb") as infile:
        original_bytes = infile.read()
        infile.seek(0)
        chunks = b""
        for chunk in iter_utf_bytes(infile, 4, "UTF-8"):
            chunks += chunk
        assert original_bytes == chunks


def test_zipfile(monkeypatch):
    """
    Test that is_zipfile returns false for a ZIP file that is accepted by
    zipfile.is_zipfile, but which can't be opened by zipfile.ZipFile.
    """
    def mocked_zipfile_init(*args):
        raise zipfile.BadZipFile("This file is not really ZIP!")

    monkeypatch.setattr('zipfile.ZipFile', mocked_zipfile_init)
    assert not is_zipfile(
        Path(
            'tests/data/application_vnd.oasis.opendocument.text/valid_1.2.odt'
        )
    )


@pytest.mark.parametrize(
    "version,expected",
    (
        ("0230", "2.3"),
        ("0231", "2.3.1"),
        ("0200", "2.0"),

        # Technically against the Exif spec, but these are tolerated.
        ("02", "2.0"),
        ("023", "2.3"),
    )
)
def test_parse_exif_version(version, expected):
    """
    Test parsing EXIF version from the original Exif value
    into a human-readable string
    """
    assert parse_exif_version(version) == expected
