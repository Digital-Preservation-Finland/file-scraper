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
        - Indexes of the streams start from 0 and correspond to the keys
          in the outer dict.
        - If the lose list contains a value some method marks as important, an
          OverlappingLoseAndImportantException is raised.
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
"""
from __future__ import unicode_literals

import six
import pytest

from file_scraper.base import BaseMeta
from file_scraper.scraper import LOSE
from file_scraper.utils import (_fill_importants,
                                _merge_to_stream, concat,
                                generate_metadata_dict, hexdigest,
                                iso8601_duration, metadata,
                                sanitize_string, strip_zeros)


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
    """Test that hexdigest returns correct sha1 and MD5 hashes."""
    if algorithm is None:
        assert hexdigest(filepath, extra_hash=extra_hash) == expected_hash
    else:
        assert hexdigest(filepath, algorithm=algorithm,
                         extra_hash=extra_hash) == expected_hash


@pytest.mark.parametrize(
    ["original_string", "sanitized_string"],
    [
        ("already sanitized", "already sanitized"),
        ("containsescape", "containsescape"),
        ("containsmultiple", "containsmultiple"),
        ("", ""),  # bell character
        ("", "")  # multiple control characters
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
    ["dict1", "method", "value", "lose", "result_dict",
     "final_importants"],
    [
        # add new key, nothing originally in importants or in lose
        ({"key1": "value1"}, "key_notimportant", "value2", [],
         {"key1": "value1", "key_notimportant": "value2"}, {}),

        ({"key1": "value1"}, "key_important", "value2", [],
         {"key1": "value1", "key_important": "value2"},
         {"key_important": "value2"}),

        ({"key1": "value1", "key3": "value3", "key4": "value4"},
         "key_important", "value2", [],
         {"key1": "value1", "key_important": "value2", "key3": "value3",
          "key4": "value4"},
         {"key_important": "value2"}),

        # add new key to an empty dict
        ({}, "key_notimportant", "value", [],
         {"key_notimportant": "value"}, {}),

        # add new key, value of which is in lose
        ({"key1": "value1"}, "key_notimportant", "value2", ["value2"],
         {"key1": "value1", "key_notimportant": "value2"}, {}),

        # add new key, value of which is None
        ({"key1": "value1"}, "key_notimportant", None, [],
         {"key1": "value1", "key_notimportant": None}, {}),

        # old value overridden by important method
        ({"key_important": "oldvalue"}, "key_important", "value1", [],
         {"key_important": "value1"},
         {"key_important": "value1"}),

        # old value is important, new one is not
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "value1", [],
         {"key_notimportant": "oldvalue"}, {"key_notimportant": "oldvalue"}),

        # old value in lose, new value not in important
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "value1",
         ["oldvalue"], {"key_notimportant": "value1"}, {}),

        # old value in lose, new value important
        ({"key_important": "oldvalue"}, "key_important", "value1",
         ["oldvalue"], {"key_important": "value1"},
         {"key_important": "value1"}),

        # key already present but new value in lose
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "newvalue",
         ["newvalue"], {"key_notimportant": "oldvalue"}, {}),

        # key already present, both old and new value in lose (old one is kept)
        ({"key_notimportant": "oldvalue"}, "key_notimportant", "newvalue",
         ["oldvalue", "newvalue"], {"key_notimportant": "oldvalue"}, {}),

        # both old and new values are important but there is no conflict
        ({"key_important": "value1", "key2": "value2"}, "key_important",
         "value1", [], {"key_important": "value1", "key2": "value2"},
         {"key_important": "value1"}),

        # Add key with None value
        ({}, "key_notimportant", None, LOSE,
         {"key_notimportant": None}, {}),

        # Add key with empty value
        ({}, "key_notimportant", "", LOSE,
         {"key_notimportant": ""}, {}),

        # Try to replace value with None when using LOSE list from scraper.
        ({"key_notimportant": "value"}, "key_notimportant", None, LOSE,
         {"key_notimportant": "value"}, {}),

        # Try to replace value with empty string when using LOSE list from
        # scraper.
        ({"key_notimportant": "value"}, "key_notimportant", "", LOSE,
         {"key_notimportant": "value"}, {}),
    ]
)
def test_merge_to_stream(dict1, method, value, lose, result_dict,
                         final_importants):
    """Test combining stream and metadata dicts."""
    # pylint: disable=too-many-arguments
    testclass = MetaTest(value)
    _merge_to_stream(dict1, getattr(testclass, method), lose,
                     final_importants)
    assert dict1 == result_dict


def test_merge_normal_conflict():
    """Test adding metadata to stream with conflicting unimportant values."""
    testclass = MetaTest("newvalue")
    with pytest.raises(ValueError) as error:
        _merge_to_stream({"key_notimportant": "oldvalue"},
                         getattr(testclass, "key_notimportant"),
                         [], {})
    assert ("Conflict with existing value 'oldvalue' and new value 'newvalue'"
            in six.text_type(error.value))


class Meta1(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta2 contain a variety of compatible and
    conflicting metadata methods that allow testing both important values
    and LOSE dict.
    """
    # pylint: disable=no-self-use

    @metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta2."""
        return 0

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta2 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta2 has."""
        return 1.0

    @metadata()
    def stream_type(self):
        """Same stream type as Meta2 has."""
        return "binary"

    @metadata()
    def key1(self):
        """
        This value conflicts with Meta2 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value1-1"

    @metadata()
    def key2(self):
        """This value is compatible with Meta2."""
        return "value2"

    @metadata()
    def key3(self):
        """This value conflicts with Meta2 and the Meta2 value is important."""
        return "key1-3"

    @metadata(important=True)
    def key4(self):
        """This value conflicts with Meta2 and this value is important."""
        return "importantvalue"


class Meta2(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta1 contain a variety of compatible and
    conflicting metadata methods that allow testing both important values
    and LOSE dict.
    """
    # pylint: disable=no-self-use

    @metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @metadata()
    def key1(self):
        """
        This value conflicts with Meta1 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value2-1"

    @metadata()
    def key2(self):
        """This value is compatible with Meta1."""
        return "value2"

    @metadata(important=True)
    def key3(self):
        """This value conflicts with Meta1 and this value is important."""
        return "key2-3"

    @metadata()
    def key4(self):
        """This value conflicts with Meta1 and the Meta1 value is important."""
        return "unimportant value"


class Meta3(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test that metadata models with different
    indices yield different streams in the metadata dict. Values of MIME type,
    version, stream_type or other metadata fields do not need to match the
    other streams.
    """
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
    def stream_type(self):
        return "audio"

    @metadata()
    def key1(self):
        return "value1"

    @metadata()
    def key2(self):
        return "value2"


class Meta4(BaseMeta):
    """
    Conflicting important value with Meta1(), where key4() is also important.
    """
    # pylint: disable=no-self-use, missing-docstring
    @metadata(important=True)
    def key4(self):
        return "conflictingvalue"


def test_merge_important_conflict():
    """Test adding metadata to stream with conflicting important values."""
    results = [[Meta1()], [Meta2()], [Meta4()]]
    with pytest.raises(ValueError) as error:
        _fill_importants(results, [])
    assert (
        "Conflict with values 'importantvalue' and 'conflictingvalue'"
        in six.text_type(error.value)
    )


def test_fill_importants():
    """Test filling the importants list"""
    results = [[Meta1()], [Meta2()], [Meta3()]]
    lose = []
    importants = _fill_importants(results, lose)
    assert importants == {"key4": "importantvalue", "key3": "key2-3"}

    lose = ["key2-3"]
    importants = _fill_importants(results, lose)
    assert importants == {"key4": "importantvalue"}


def test_generate_metadata_dict():
    """Test generating metadata dict using the metadata objects."""
    results = [[Meta1()], [Meta2()], [Meta3()]]
    lose = ["value2-1"]
    metadata_dict = generate_metadata_dict(results, lose)
    assert metadata_dict == {0: {"index": 0, "key1": "value1-1",
                                 "key2": "value2", "key3": "key2-3",
                                 "key4": "importantvalue",
                                 "mimetype": "mime", "version": 1.0,
                                 "stream_type": "binary"},
                             1: {"index": 1, "key1": "value1",
                                 "key2": "value2", "mimetype": "anothermime",
                                 "version": 2, "stream_type": "audio"}}


def test_concat():
    """Test concat function."""
    assert concat([]) == ""
    assert concat(["test"]) == "test"
    assert concat(["test1", "test2"]) == "test1\ntest2"
    assert concat([], "prefix:") == ""
    assert concat(["test"], "prefix:") == "prefix:test"
    assert (concat(["test1", "test2"], "prefix:") ==
            "prefix:test1\nprefix:test2")
