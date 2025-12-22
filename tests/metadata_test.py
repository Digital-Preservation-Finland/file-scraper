"""
Tests for the metadata module.

These are the requirements for the metadata functions:
requirements:
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
    - _merge_functions_to_stream
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
    - merge_normal_conflict
        - Adding non-important metadata causes conflict error when another
          value already exists in stream.
    - merge_important_conflict
        - Adding important value causes conflict error when another important
          value already exists in stream.
    - fill_importants
        - Important values are resulted as important
        - Lose values marked as important are not important
    - generate_metadata_dict
        - A dict with metadata method names as keys and return values as values
          is returned with priority of conflicting values determined correctly
          based on the given lose list and importantness of the methods.
        - Indexes of the streams start from 0 and correspond to the keys
          in the outer dict.
        - If the lose list contains a value some method marks as important, an
          OverlappingLoseAndImportantException is raised.
"""

import pytest

from file_scraper.base import BaseMeta
from file_scraper.scraper import LOSE
from file_scraper.metadata import (
    _merge_functions_to_stream,
    generate_metadata_dict,
)


class Meta1(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This class is associated with Meta2.

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta2 contain a variety of compatible and
    conflicting metadata methods.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta2."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta2 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta2 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta2 has."""
        return "binary"

    @BaseMeta.metadata()
    def key1(self):
        """
        This value conflicts with Meta2 and neither is important.

        This method can be used to test the LOSE dict.
        """
        return "value1-1"

    @BaseMeta.metadata()
    def key2(self):
        """This value is compatible with Meta2."""
        return "value2"

    @BaseMeta.metadata()
    def key3(self):
        """This value conflicts with Meta2 and the Meta2 value is important."""
        return "value1-3"

    @BaseMeta.metadata()
    def key4(self):
        """This value conflicts with Meta2 and this value is important."""
        return "value4"


class Meta2(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This class is associated with Meta1

    This metadata class is used to test merging two metadata models with
    identical indices. This and Meta1 contain a variety of compatible and
    conflicting metadata methods.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"

    @BaseMeta.metadata()
    def key1(self):
        """
        This value conflicts with Meta1.

        This method can be used to test overwriting.
        """
        return "value2-1"

    @BaseMeta.metadata()
    def key2(self):
        """This value is compatible with Meta1."""
        return "value2"

    @BaseMeta.metadata()
    def key3(self):
        """This value conflicts with Meta1"""
        return "value2-3"

    @BaseMeta.metadata()
    def key4(self):
        """This value conflicts with Meta1"""
        return "conflicting value"


class Meta3(BaseMeta):
    """
    Identical metadata with Meta1. Used for testing that results
    can be merged to scraper.stream without conflicts.
    """
    @BaseMeta.metadata()
    def index(self):
        """Return 0: this metadata class will be merged with Meta1."""
        return 0

    @BaseMeta.metadata()
    def mimetype(self):
        """Same MIME type as Meta1 has."""
        return "mime"

    @BaseMeta.metadata()
    def version(self):
        """Same version as Meta1 has."""
        return 1.0

    @BaseMeta.metadata()
    def stream_type(self):
        """Same stream type as Meta1 has."""
        return "binary"


class Meta4(BaseMeta):
    """
    Metadata class for testing generate_metadata_dict().

    This metadata class is used to test that metadata models with different
    indices yield different streams in the metadata dict. Values of MIME type,
    version, stream_type or other metadata fields do not need to match the
    other streams.
    """

    @BaseMeta.metadata()
    def index(self):
        """Return stream index"""
        return 1

    @BaseMeta.metadata()
    def mimetype(self):
        """Return MIME type"""
        return "anothermime"

    @BaseMeta.metadata()
    def version(self):
        """Return version"""
        return 2

    @BaseMeta.metadata()
    def stream_type(self):
        """Return stream type"""
        return "audio"

    @BaseMeta.metadata()
    def key1(self):
        """Return metadata"""
        return "value1"

    @BaseMeta.metadata()
    def key2(self):
        """Return metadata"""
        return "value2"


class MetaTest:
    """A collection of metadata methods for testing purposes."""

    def __init__(self, value):
        """
        Initialize test metadata model

        :value: Attribute value to return in metadata methods
        """
        self.value = value

    @BaseMeta.metadata()
    def index(self):
        return 0

    @BaseMeta.metadata()
    def a_function(self):
        """Not important metadata"""
        return self.value

    @BaseMeta.metadata()
    def another_function(self):
        """Important metadata"""
        return self.value


@pytest.mark.parametrize(
    ["meta_dict", "method", "value", "lose"],
    [
        # add new key to an empty dict
        (
            {},
            "a_function",
            "value",
            [],
        ),
        # add new key, value of which is in lose
        (
            {"key1": "value1"},
            "a_function",
            "value2",
            ["value2"],
        ),
        # add new key, value of which is None
        (
            {"key1": "value1"},
            "a_function",
            None,
            [],
        ),
        # key already present but new value in lose
        (
            {},
            "a_function",
            "newvalue",
            ["newvalue"],
        ),
        # key already present, both old and new value in lose (old one is kept)
        (
            {},
            "a_function",
            "newvalue",
            ["oldvalue", "newvalue"],
        ),
        # Add key with None value
        ({}, "a_function", None, LOSE),
        # Add key with empty value
        (
            {},
            "a_function",
            "",
            LOSE,
        ),
        # Try to replace value with None when using LOSE list from scraper.
        (
            {},
            "a_function",
            None,
            LOSE,
        ),
        # Try to replace value with empty string when using LOSE list from
        # scraper.
        (
            {},
            "a_function",
            "",
            LOSE,
        ),
    ],
)
def test_merge_functions_to_stream(
    meta_dict,
    method,
    value,
    lose,
):
    """
    Test combining stream and metadata dicts.

    :meta_dict: Stream metadata dict
    :method: Method name which result will be merged
    :lose: Lose values
    :result_dict: Resulted stream metadata after merge
    :final_importants: Resulted important metadata
    """
    # pylint: disable=too-many-arguments
    testclass = MetaTest(value)
    result_dict = meta_dict
    result_dict["a_function"] = getattr(MetaTest(value), method, None)
    meta_dict["index"], result_dict["index"] = 0, 0
    _merge_functions_to_stream(meta_dict, getattr(testclass, method), lose)
    assert len(meta_dict) == len(result_dict)
    assert meta_dict == result_dict


def test_merge_normal_conflict():
    """Test adding metadata to stream with conflicting unimportant values."""
    prev_test_class = MetaTest("oldvalue")
    new_class = MetaTest("newvalue")
    with pytest.raises(ValueError) as error:
        _merge_functions_to_stream(
            {"index": 0, "a_function": prev_test_class.a_function},
            getattr(new_class, "a_function"),
            [],
        )
    assert "Failed to merge the metadata" in str(error.value)


@pytest.mark.parametrize(
    ("meta_classes", "lose", "valid_dict", "expected_conflict_values"),
    [
        (
            [Meta1, Meta4], ["value2-1"], True, []),
        (
            [Meta1, Meta2, Meta4],
            [None],
            False,
            [
                {
                    "metadata": "key1",
                    "overwriting_model": "Meta2",
                    "overwriting_value": "value2-1",
                    "current_model": "Meta1",
                    "current_value": "value1-1",
                },
                {
                    "metadata": "key3",
                    "overwriting_model": "Meta2",
                    "overwriting_value": "value2-3",
                    "current_model": "Meta1",
                    "current_value": "value1-3",
                },
                {
                    "metadata": "key4",
                    "overwriting_model": "Meta2",
                    "overwriting_value": "conflicting value",
                    "current_model": "Meta1",
                    "current_value": "value4",
                },
            ],
        ),
        (
            [Meta1, Meta2, Meta4],
            ["value2-1"],
            False,
            [
                {
                    "metadata": "key3",
                    "overwriting_model": "Meta2",
                    "overwriting_value": "value2-3",
                    "current_model": "Meta1",
                    "current_value": "value1-3",
                },
                {
                    "metadata": "key4",
                    "overwriting_model": "Meta2",
                    "overwriting_value": "conflicting value",
                    "current_model": "Meta1",
                    "current_value": "value4",
                },
            ],
        ),
    ],
)
def test_generate_metadata_dict(
        meta_classes, lose, valid_dict, expected_conflict_values
):
    """Test generating metadata dict using the metadata objects.
    Tests both a successful case and a case with conflicts in
    metadata. The case
    """
    results = []
    expected_conflicts = []
    for dictionary in expected_conflict_values:
        expected_conflicts.append(
            f"Failed to merge the metadata '{dictionary['metadata']}' from "
            f"the model '{dictionary['overwriting_model']}' "
            f"with a value of '{dictionary['overwriting_value']}' to the "
            f"stream. The existing stream metadata was produced by "
            f"the model '{dictionary['current_model']}' with a value "
            f"'{dictionary['current_value']}'."
        )
    for meta_class in meta_classes:
        results.append([meta_class()])
    (metadata_dict, conflicts) = generate_metadata_dict(results, lose)
    if valid_dict:
        assert metadata_dict == {
            0: {
                "index": 0,
                "key1": "value1-1",
                "key2": "value2",
                "key3": "value1-3",
                "key4": "value4",
                "mimetype": "mime",
                "version": 1.0,
                "stream_type": "binary",
            },
            1: {
                "index": 1,
                "key1": "value1",
                "key2": "value2",
                "mimetype": "anothermime",
                "version": 2,
                "stream_type": "audio",
            },
        }
    assert conflicts == expected_conflicts
