"""Tests for utils.py"""

import pytest

from file_scraper.utils import hexdigest, sanitize_string,\
        iso8601_duration, strip_zeros, combine_metadata, run_command


@pytest.mark.parametrize(
    ["filepath", "extra_hash", "expected_hash"],
    [
        ("tests/data/text_plain/valid__utf8.txt", None,
         "a0d01fcbff5d86327d542687dcfd8b299d054147"),
        ("tests/data/image_png/valid_1.2.png", None,
         "a7947ca260c313a4e7ece2312fd25db6cbcb9283"),
        ("tests/data/text_plain/valid__utf8.txt", "abc123",
         "c7a2bcf3dc77cdae5b59dc9afbc7c4f1cc375b0f")
    ]
)
def test_hexdigest(filepath, extra_hash, expected_hash):
    """Test that hexdigest returns correct sha1 hashes"""

    assert hexdigest(filepath, extra_hash=extra_hash) == expected_hash

@pytest.mark.parametrize(
    ["original_string", "sanitized_string"],
    [
        (u"already sanitized", "already sanitized"),
        (u"containsescape", "containsescape"),
        (u"", "") # bell character
    ]
)
def test_sanitize_string(original_string, sanitized_string):
    """Test sanitize_string"""
    assert sanitize_string(original_string) == sanitized_string


@pytest.mark.parametrize(
    ["seconds", "expected_output"],
    [
        (0, "PT0S"),
        (0.01, "PT0.01S"),
        (0.001, "PT0S"),
        (0.005, "PT0.01S"),
        (1, "PT1S"),
        (59.99, "PT59.99S"),
        (59.999, "PT1M"),
        (60, "PT1M"),
        (61, "PT1M1S"),
        (119.99, "PT1M59.99S"),
        (119.999, "PT2M"),
        (3599, "PT59M59S"),
        (3600, "PT1H"),
        (3600.001, "PT1H"),
        (3601, "PT1H1S"),
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
        ("123.000", "123"),
        ("123.0", "123"),
        ("450.0", "450"),
        ("450", "450"),
        ("0123.0", "0123"),
        ("1000000", "1000000"),
        ("1_000_000", "1_000_000"),
        ("1_234_000.0", "1_234_000")
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

        # Index in the inner metadata dict does not match stream key
        ({0: {"key1": "value1", "index": 0}},
         {1: {"key2": "value2", "index": 0}},
         [], None,
         {0: {"key1": "value1", "index": 0},
          1: {"key2": "value2", "index": 0}}),

        # Index in the inner metadata dict matches stream key
        ({1: {"key1": "value1", "index": 0}},
         {0: {"key2": "value2", "index": 0}},
         [], None,
         {1: {"key1": "value1", "key2": "value2", "index": 0}}),

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
         {0: {"key1": "value1", "key2": "value2", "commonkey": "importantvalue",
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


def test_combine_metadata_conflict():
    """
    Test that combine_metadata raises a ValueError when there is unresolved
    conflict in the two dicts.
    """
    with pytest.raises(ValueError) as error:
        combine_metadata({0: {"key": "value1", "index": 0}},
                         {0: {"key": "value2", "index": 0}})
    assert "Conflict with existing value" in str(error.value)


def test_run_command():
    """-""" #TODO add tests and docstring
    pass
