"""Module to test the default constants that were set."""

import pytest

from file_scraper.defaults import PRONOM_DICT, VERSION_DICT


@pytest.mark.parametrize(
    ["constant_dict", "expected_type"],
    [
        [PRONOM_DICT, tuple],
        [VERSION_DICT, dict],
    ]
)
def test_constants_syntax(constant_dict, expected_type):
    """A simple test to ensure that the two complicated constants, PRONON_DICT
    and VERSION_DICT, will have appropriate type for their value.
    """
    for value in constant_dict.values():
        assert isinstance(value, expected_type)
