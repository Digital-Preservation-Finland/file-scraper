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
    - combine_metadata
        - A new dict containing keys from both given dicts is returned.
        - Unique keys and their values in the inner dicts are all present in
          the returned dict within their corresponding stream dict.
        - 'important' dict has no effect unless there is a conflict between
          the two dicts that are to be combined.
        - If a key is present in both dicts but its values differ:
            - if the key is present only in the important dict, the value form
              important is used in the returned dict.
            - if the key is present on in the lose list, the value from
              metadata dict is used in the returned dict.
            - if the key is present in both important and lose, the value from
              stream dict is used in the returned dict.
            - if the key is not present in important or lose, a ValueError
              with message "Conflict with existing value" is raised
        - If either metadata or stream dict is None, a new dict containing the
          contents of the other dict is returned.
        - Neither metadata nor stream dict is modified in-place.
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
"""

import os
from tempfile import TemporaryFile
import pytest

from file_scraper.utils import hexdigest, sanitize_string,\
    iso8601_duration, strip_zeros, combine_metadata, run_command


@pytest.mark.parametrize(
    ["filepath", "extra_hash", "algorithm", "expected_hash"],
    [
        ("tests/data/text_plain/valid__utf8.txt", None, None,
         "a0d01fcbff5d86327d542687dcfd8b299d054147"),
        ("tests/data/image_png/valid_1.2.png", None, 'SHA-1',
         "a7947ca260c313a4e7ece2312fd25db6cbcb9283"),
        ("tests/data/text_plain/valid__utf8.txt", "abc123", None,
         "c7a2bcf3dc77cdae5b59dc9afbc7c4f1cc375b0f"),
        ("tests/data/image_png/valid_1.2.png", None, 'MD5',
         "ce778faab1d293275a471df03faecdcd")
    ]
)
def test_hexdigest(filepath, extra_hash, algorithm, expected_hash):
    """Test that hexdigest returns correct sha1 and MD5 hashes"""
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
    """Test sanitize_string"""
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
    """
    Test that for a given duration in seconds, a corresponding string
    containing PT[hh]H[mm]M[ss]S is returned
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
    Test that trailing zeroes (and only them) are stripped from a string
    representation of a float
    """

    assert strip_zeros(float_str) == expected_output


@pytest.mark.parametrize(
    ["dict1", "dict2", "lose", "important", "result_dict"],
    [
        # "normal" case
        ({0: {"key1": "value1", "index": 0}},
         {0: {"key2": "value2", "index": 0}},
         [], None,
         {0: {"key1": "value1", "key2": "value2", "index": 0}}),

        # "normal" case with more items
        ({0: {"key1-1": "value1-1", "key1-2": "value1-2", "index": 0}},
         {0: {"key2-1": "value2-1", "key2-2": "value2-2", "index": 0}},
         [], None,
         {0: {"key1-1": "value1-1", "key1-2": "value1-2",
              "key2-1": "value2-1", "key2-2": "value2-2", "index": 0}}),

        # "normal" case with more streams in metadata dict
        ({0: {"key1": "value1", "index": 0},
          1: {"key3": "value3", "index": 1}},
         {0: {"key2": "value2", "index": 0}},
         [], None,
         {0: {"key1": "value1", "key2": "value2", "index": 0},
          1: {"key3": "value3", "index": 1}}),

        # "normal" case with more streams in stream dict
        ({0: {"key1": "value1", "index": 0}},
         {0: {"key2": "value2", "index": 0},
          1: {"key3": "value3", "index": 1}},
         [], None,
         {0: {"key1": "value1", "key2": "value2", "index": 0},
          1: {"key3": "value3", "index": 1}}),

        # no conflict but an important key
        ({0: {"key1": "value1", "importantkey": "dullvalue", "index": 0}},
         {0: {"key2": "value2", "index": 0}},
         [], {"importantkey": "importantvalue"},
         {0: {"key1": "value1", "key2": "value2",
              "importantkey": "dullvalue", "index": 0}}),

        # conflict: conflicting key in lose
        ({0: {"key1": "value1", "commonkey": "commonvalue1", "index": 0}},
         {0: {"key2": "value2", "commonkey": "commonvalue2", "index": 0}},
         ["commonvalue1"], None,
         {0: {"key1": "value1", "key2": "value2", "commonkey": "commonvalue2",
              "index": 0}}),

        # conflict: conflicting key in important
        ({0: {"key1": "value1", "commonkey": "commonvalue1", "index": 0}},
         {0: {"key2": "value2", "commonkey": "commonvalue2", "index": 0}},
         [], {"commonkey": "importantvalue"},
         {0: {"key1": "value1", "key2": "value2",
              "commonkey": "importantvalue",
              "index": 0}}),

        # conflict: conflicting key in both lose and  important
        ({0: {"key1": "value1", "commonkey": "commonvalue1", "index": 0}},
         {0: {"key2": "value2", "commonkey": "commonvalue2", "index": 0}},
         ["importantvalue", "commonvalue2"], {"commonkey": "importantvalue"},
         {0: {"key1": "value1", "key2": "value2",
              "commonkey": "commonvalue1",
              "index": 0}}),

        # no metadata
        ({0: {"key1-1": "value1-1", "key1-2": "value1-2", "index": 0}},
         None, [], None,
         {0: {"key1-1": "value1-1", "key1-2": "value1-2", "index": 0}}),

        # no stream
        (None,
         {0: {"key2-1": "value2-1", "key2-2": "value2-2", "index": 0}},
         [], None,
         {0: {"key2-1": "value2-1", "key2-2": "value2-2", "index": 0}})
    ]
)
def test_combine_metadata(dict1, dict2, lose, important, result_dict):
    """
    Test that all allowed use cases of combining stream and metadata
    dicts are handled correctly.
    """
    assert (combine_metadata(dict1, dict2, lose=lose, important=important)
            == result_dict)
    for origdict in [dict1, dict2]:
        if origdict is not None:
            origdict["newkey"] = "newvalue"
            assert origdict != result_dict


def test_combine_metadata_conflict():
    """
    Test that combine_metadata raises a ValueError when there is unresolved
    conflict in the two dicts.
    """
    with pytest.raises(ValueError) as error:
        combine_metadata({0: {"key": "value1", "index": 0}},
                         {0: {"key": "value2", "index": 0}})
    assert "Conflict with existing value" in str(error.value)


@pytest.mark.parametrize(
    ["command", "expected_statuscode", "expected_stdout", "expected_stderr"],
    [
        (["echo", "testing"], 0, "testing\n", ""),
        (["seq", "5"], 0, "1\n2\n3\n4\n5\n", ""),
        (["cd", "nonexistentdir"], 1, [""],
         "/usr/bin/cd: line 2: cd: nonexistentdir: No such file or directory\n"
        )
    ]
)
def test_run_command(command, expected_statuscode, expected_stdout,
                     expected_stderr):
    """
    Test running commands normally: without directing stdout to a file or using
    custom environment
    """
    (statuscode, stdout, stderr) = run_command(command)
    assert statuscode == expected_statuscode
    assert stderr == expected_stderr

    for line_number, line in enumerate(stdout):
        assert line == expected_stdout[line_number]


def test_run_command_to_file():
    """Test having output of a shell command directed to a file"""
    with TemporaryFile() as outfile:
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
    """Test using custom environment variables"""
    custom_env = os.environ.copy()
    custom_env["TEST_VARIABLE"] = "testing"
    (statuscode, stdout, stderr) = run_command(["printenv", "TEST_VARIABLE"],
                                               env=custom_env)

    assert stdout == "testing\n"
    assert statuscode == 0
    assert not stderr
