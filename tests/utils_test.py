"""
Tests for utils.py

This module tests the following utility functions:
    - hexdigest
        - Returns the hash of the given file, both for text and binary data.
        - Defaults to SHA-1 algorithm for calculating the hash.
        - MD5 algorithm can also be used.
        - An extra hash can be given to the function and this extra hash is
          appended to the file in calculation
    - sanitize_string
        - For strings without any non-printable control characters, the
          original string is returned.
        - For strings containing one or more control characters, a new string
          without the control character(s) is returned.
        - For strings consisting of control characters, an empty string is
          returned.
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
    - strip_zeros
        - When there are no zeros to be stripped in the input, the output is
          identical.
        - One or more trailing zeros from the decimal part are removed from
          the returned string.
        - Non-trailing zeros in the decimal part are not affected.
        - If nothing is left in the decimal part, decimal point is also removed
          from the returned string.
        - Trailing zeros in the integer part are not affected.
        - Leading zeros are not affected.
        - Underscores in the input do not affect the stripping, e.g.
          "1_000_000" is not altered but for "1_234_000.000_000", "1_234_000"
          is returned.
    - _merge_to_stream
        - Value returned by the given metadata method is or is not added to
          the given metadata dict with the method name as the key under the
          following conditions:
            - If the key is not present, a new key is always added whether the
              value is in lose dict or not.
            - If the key is already present but not important and the new
              method is important, the old value is replaced by the new one.
            - If the old value is important and the new one is not, the old
              value is not replaced.
            - If the old value is present in the lose list, the new value
              replaces it whether the new one is important or not.
            - If the new value is present in the lose list and the old one is
              not, the old value is kept.
            - When old and new value are identical, no exceptions are raised
              and the value is kept as is.
            - If old and new values differ aind neither is important nor in
              lose, ValueError is raised.
            - If old and new values differ and both are important, ValueError
              is raised.
        - If the method is important, the entry is also added to the importants
          dict.
    - generate_metadata_dict
        - A dict with metadata method names as keys and return values as values
          is returned with priority of conflicting values determined correctly
          based on the given lose list and importantness of the methods.
        - Container metadata consisting of mimetype and version is found in the
          zero stream.
        - Indexes of the other streams start from 1 and correspond to the keys
          in the outer dict.
        - If the lose list contains a value some method marks as important, an
          OverlappingLoseAndImportantException is raised.
    - run_command
        - Given command is run and its statuscode is returned as the first
          member of the returned tuple.
        - If no stdout file is given, the output of the command is returned
          as the second member of the returned tuple.
        - The stderr output of t he command is returned as the third member
          of the returned tuple.
        - If a stdout file is given, the stdout output of the command is
          recorded in that file.
        - If custom environment variables are supplied, they are used when
          running the command.
    - concat
        - Concatenation of strings or empty lists with and without prefix
"""

import os
from tempfile import TemporaryFile
import pytest

from file_scraper.base import BaseMeta
from file_scraper.utils import hexdigest, sanitize_string,\
    iso8601_duration, strip_zeros, run_command, concat,\
    metadata, _merge_to_stream, generate_metadata_dict,\
    OverlappingLoseAndImportantException


@pytest.mark.parametrize(
    ["filepath", "extra_hash", "algorithm", "expected_hash"],
    [
        ("tests/data/text_plain/valid__utf8.txt", None, None,
         "a0d01fcbff5d86327d542687dcfd8b299d054147"),
        ("tests/data/image_png/valid_1.2.png", None, 'SHA-1',
         "a7947ca260c313a4e7ece2312fd25db6cbcb9283"),
        ("tests/data/text_plain/valid__utf8.txt", b"abc123", None,
         "c7a2bcf3dc77cdae5b59dc9afbc7c4f1cc375b0f"),
        ("tests/data/image_png/valid_1.2.png", None, 'MD5',
         "ce778faab1d293275a471df03faecdcd")
    ]
)
def test_hexdigest(filepath, extra_hash, algorithm, expected_hash):
    """Test that hexdigest returns correct sha1 and MD5 hashes."""
    if algorithm is None:
        assert hexdigest(filepath, extra_hash=extra_hash) == expected_hash
    else:
        assert hexdigest(filepath, algorithm=algorithm,
                         extra_hash=extra_hash) == expected_hash


@pytest.mark.parametrize(
    ["original_string", "sanitized_string"],
    [
        (u"already sanitized", "already sanitized"),
        (u"containsescape", "containsescape"),
        (u"containsmultiple", "containsmultiple"),
        (u"", ""),  # bell character
        (u"", "")  # multiple control characters
    ]
)
def test_sanitize_string(original_string, sanitized_string):
    """Test sanitize_string."""
    assert sanitize_string(original_string) == sanitized_string


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
    """Test stripping zeros from string representation of a float."""

    assert strip_zeros(float_str) == expected_output


class MetaTest(object):
    """A collection of metadata methods for testing purposes."""
    # pylint: disable=no-self-use, missing-docstring

    def __init__(self, value):
        self.value = value

    @metadata()
    def key_notimportant(self):
        return self.value

    @metadata(important=True)
    def key_important(self):
        return self.value


@pytest.mark.parametrize(
    ["dict1", "method", "value", "lose", "importants", "result_dict",
     "final_importants"],
    [
        # add new key, nothing originally in importants or in lose
        ({"key1": "value1"}, "key_notimportant", "value2", [], {},
         {"key1": "value1", "key_notimportant": "value2"}, {}),

        ({"key1": "value1"}, "key_important", "value2", [], {},
         {"key1": "value1", "key_important": "value2"},
         {"key_important": "value2"}),

        ({"key1": "value1", "key3": "value3", "key4": "value4"},
         "key_important", "value2", [], {},
         {"key1": "value1", "key_important": "value2", "key3": "value3",
          "key4": "value4"},
         {"key_important": "value2"}),

        # add new key to an empty dict
        ({}, "key_notimportant", "value", [], {},
         {"key_notimportant": "value"}, {}),

        # add new key, value of which is in lose
        ({"key1": "value1"}, "key_notimportant", "value2", ["value2"], {},
         {"key1": "value1", "key_notimportant": "value2"}, {}),

        # add new key, value of which is None
        ({"key1": "value1"}, "key_notimportant", None, [], {},
         {"key1": "value1", "key_notimportant": None}, {}),

        # old value overridden by important method
        ({"key_important": "oldvalue"}, "key_important", "value1", [], {},
         {"key_important": "value1"},
         {"key_important": "value1"}),

        # old value is important, new one is not
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "value1", [],
         {"key_notimportant": "oldvalue"}, {"key_notimportant": "oldvalue"},
         {"key_notimportant": "oldvalue"}),

        # old value in lose, new value not in important
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "value1",
         ["oldvalue"], {}, {"key_notimportant": "value1"}, {}),

        # old value in lose, new value important
        ({"key_important": "oldvalue"}, "key_important", "value1",
         ["oldvalue"], {}, {"key_important": "value1"},
         {"key_important": "value1"}),

        # key already present but new value in lose
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "newvalue",
         ["newvalue"], {}, {"key_notimportant": "oldvalue"}, {}),

        # key already present, both old and new value in lose (old one is kept)
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "newvalue",
         ["oldvalue", "newvalue"], {}, {"key_notimportant": "oldvalue"}, {}),

        # both old and new values are important but there is no conflict
        ({"key_important": "value1", "key2": "value2"}, "key_important",
         "value1", [], {"key_important": "value1"},
         {"key_important": "value1", "key2": "value2"},
         {"key_important": "value1"}),
    ]
)
def test_merge_to_stream(dict1, method, value, lose, importants, result_dict,
                         final_importants):
    """Test combining stream and metadata dicts."""
    # pylint: disable=too-many-arguments
    testclass = MetaTest(value)
    _merge_to_stream(dict1, getattr(testclass, method), lose, importants)
    assert dict1 == result_dict
    assert importants == final_importants


def test_merge_normal_conflict():
    """Test adding metadata to stream with conflicting unimportant values."""
    testclass = MetaTest("newvalue")
    with pytest.raises(ValueError) as error:
        _merge_to_stream({"key_notimportant": "oldvalue"},
                         getattr(testclass, "key_notimportant"),
                         [], {})
    assert ("Conflict with existing value 'oldvalue' and new value 'newvalue'"
            in str(error.value))


def test_merge_important_conflict():
    """Test adding metadata to stream with conflicting important values."""
    testclass = MetaTest("newvalue")
    with pytest.raises(ValueError) as error:
        _merge_to_stream({"key_important": "oldvalue"},
                         getattr(testclass, "key_important"),
                         [], {"key_important": "oldvalue"})
    assert "Conflict with values 'oldvalue' and 'newvalue'" in str(error.value)


class Meta1(BaseMeta):
    """Metadata class for testing generate_metadata_dict()"""
    # pylint: disable=no-self-use, missing-docstring

    @metadata()
    def index(self):
        return 0

    @metadata()
    def mimetype(self):
        return "mime"

    @metadata()
    def version(self):
        return 1.0

    @metadata()
    def key1(self):
        return "value1-1"

    @metadata()
    def key2(self):
        return "value2"

    @metadata()
    def key3(self):
        return "key1-3"

    @metadata(important=True)
    def key4(self):
        return "importantvalue"


class Meta2(BaseMeta):
    """Metadata class for testing generate_metadata_dict()"""
    # pylint: disable=no-self-use, missing-docstring

    @metadata()
    def index(self):
        return 0

    @metadata()
    def mimetype(self):
        return "mime"

    @metadata()
    def version(self):
        return 1.0

    @metadata()
    def key1(self):
        return "value2-1"

    @metadata()
    def key2(self):
        return "value2"

    @metadata(important=True)
    def key3(self):
        return "key2-3"

    @metadata()
    def key4(self):
        return "unimportant value"


class Meta3(BaseMeta):
    """Metadata class for testing generate_metadata_dict()"""
    # pylint: disable=no-self-use, missing-docstring

    @metadata()
    def index(self):
        return 1

    @metadata()
    def mimetype(self):
        return "anothermime"

    @metadata()
    def version(self):
        return 2

    @metadata()
    def key1(self):
        return "value1"

    @metadata()
    def key2(self):
        return "value2"


def test_generate_metadata_dict():
    """Test generating metadata dict using the metadata objects."""
    results = [[Meta1()], [Meta2()], [Meta3()]]
    lose = ["value2-1"]
    metadata_dict = generate_metadata_dict(results, lose)
    assert metadata_dict == {0: {"index": 0, "mimetype": "mime",
                                 "version": 1.0},
                             1: {"index": 1, "key1": "value1-1",
                                 "key2": "value2", "key3": "key2-3",
                                 "key4": "importantvalue",
                                 "mimetype": "mime", "version": 1.0},
                             2: {"index": 2, "key1": "value1",
                                 "key2": "value2", "mimetype": "anothermime",
                                 "version": 2}}


def test_overlapping_error():
    """Test that important values within the lose list cause an exception."""
    results = [[Meta2()]]
    lose = ["key2-3"]
    with pytest.raises(OverlappingLoseAndImportantException) as e_info:
        generate_metadata_dict(results, lose)
    assert ("The given lose dict contains values that are marked as important"
            in str(e_info.value))


@pytest.mark.parametrize(
    ["command", "expected_statuscode", "expected_stdout", "expected_stderr"],
    [
        (["echo", "testing"], 0, b"testing\n", ""),
        (["seq", "5"], 0, b"1\n2\n3\n4\n5\n", ""),
        (["cd", "nonexistentdir"], 1, "",
         b"/usr/bin/cd: line 2: cd: nonexistentdir: No such file or directory\n"
        )
    ]
)
def test_run_command(command, expected_statuscode, expected_stdout,
                     expected_stderr):
    """Test running commands normally."""
    (statuscode, stdout, stderr) = run_command(command)
    assert statuscode == expected_statuscode
    assert stderr == expected_stderr

    for line_number, line in enumerate(stdout):
        assert line == expected_stdout[line_number]


def test_run_command_to_file():
    """Test having output of a shell command directed to a file"""
    with TemporaryFile('w+') as outfile:
        (statuscode, stdout, stderr) = run_command(
            ["seq", "5"], stdout=outfile)

        assert statuscode == 0
        assert not stdout
        assert not stderr

        outfile.seek(0)
        expected_number = 1
        for line in outfile:
            assert line == str(expected_number) + '\n'
            expected_number += 1


def test_run_command_with_env():
    """Test running commands using custom environment variables."""
    custom_env = os.environ.copy()
    custom_env["TEST_VARIABLE"] = "testing"
    (statuscode, stdout, stderr) = run_command(["printenv", "TEST_VARIABLE"],
                                               env=custom_env)

    assert stdout == b"testing\n"
    assert statuscode == 0
    assert not stderr


def test_concat():
    """Test concat function."""
    assert concat([]) == ''
    assert concat(['test']) == 'test'
    assert concat(['test', 'test']) == 'test\ntest'
    assert concat([], 'prefix:') == ''
    assert concat(['test'], 'prefix:') == 'prefix:test'
    assert concat(['test', 'test'], 'prefix:') == 'prefix:test\nprefix:test'
