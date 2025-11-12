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

from itertools import chain

from file_scraper.scraper import LOSE
from file_scraper.metadata import (
    _fill_importants,
    _merge_to_stream,
    generate_metadata_dict,
    metadata,
    )


class MetaTest:
    """A collection of metadata methods for testing purposes."""

    def __init__(self, value):
        """
        Initialize test metadata model

        :value: Attribute value to return in metadata methods
        """
        self.value = value

    @metadata()
    def key_notimportant(self):
        """Not important metadata"""
        return self.value

    @metadata(important=True)
    def key_important(self):
        """Important metadata"""
        return self.value


@pytest.mark.parametrize(
    ["meta_dict", "method", "value", "lose", "result_dict",
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
def test_merge_to_stream(meta_dict, method, value, lose, result_dict,
                         final_importants):
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
    _merge_to_stream(meta_dict, getattr(testclass, method), lose,
                     final_importants)
    assert meta_dict == result_dict


def test_merge_normal_conflict():
    """Test adding metadata to stream with conflicting unimportant values."""
    testclass = MetaTest("newvalue")
    with pytest.raises(ValueError) as error:
        _merge_to_stream({"key_notimportant": "oldvalue"},
                         getattr(testclass, "key_notimportant"),
                         [], {})
    assert ("Conflict with values 'oldvalue' and 'newvalue'"
            in str(error.value))


def test_merge_important_conflict(meta_class_fx):
    """Test adding metadata to stream with conflicting important
    value."""
    model = meta_class_fx('meta4')
    importants = {
        'key4': 'importantvalue'
    }
    with pytest.raises(ValueError) as error:
        _fill_importants(model.key4, importants, [])
    assert (
        "Conflict with values 'importantvalue' and 'conflictingvalue'"
        in str(error.value)
    )


def test_fill_importants(meta_class_fx):
    """Test filling the importants list"""
    results = [[meta_class_fx('meta1')],
               [meta_class_fx('meta2')],
               [meta_class_fx('meta3')]]
    lose = []
    importants = {}
    for model in chain.from_iterable(results):
        for method in model.iterate_metadata_methods():
            _fill_importants(method, importants, lose)
    assert importants == {"key4": "importantvalue", "key3": "key2-3"}

    lose = ["key2-3"]
    importants = {}
    for model in chain.from_iterable(results):
        for method in model.iterate_metadata_methods():
            _fill_importants(method, importants, lose)
    assert importants == {"key4": "importantvalue"}


@pytest.mark.parametrize(
    ('meta_classes', 'lose', 'valid_dict', 'expected_conflicts'),
    [
        (['meta1', 'meta2', 'meta3'], ["value2-1"], True, []),
        (['meta1', 'meta2', 'meta3'], [None], False,
         ["Conflict with values 'value1-1' and 'value2-1' for 'key1'."]),
        (['meta1', 'meta2', 'meta4'], ["value2-1"], False,
         ["Conflict with values 'importantvalue' and 'conflictingvalue' for "
          "'key4': both are marked important."])
    ],
    ids=('Successful merge, only conflicting value is in lose',
         'Unsuccessful merge, conflicting value is not in lose',
         'Unsuccessful merge, conflicts in important values')
)
def test_generate_metadata_dict(
        meta_class_fx, meta_classes, lose, valid_dict, expected_conflicts):
    """Test generating metadata dict using the metadata objects.
    Tests both a successful case and a case with conflicts in
    metadata, both while filling import values and while merging the
    results.
    """
    results = []
    for meta_class in meta_classes:
        results.append([meta_class_fx(meta_class)])
    (metadata_dict, conflicts) = generate_metadata_dict(results, lose)
    if valid_dict:
        assert metadata_dict == {0: {"index": 0, "key1": "value1-1",
                                     "key2": "value2", "key3": "key2-3",
                                     "key4": "importantvalue",
                                     "mimetype": "mime", "version": 1.0,
                                     "stream_type": "binary"},
                                 1: {"index": 1, "key1": "value1",
                                     "key2": "value2",
                                     "mimetype": "anothermime",
                                     "version": 2, "stream_type": "audio"}}
    assert conflicts == expected_conflicts
