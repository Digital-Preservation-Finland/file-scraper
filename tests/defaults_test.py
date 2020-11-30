# -*- coding: utf-8 -*-
"""Module to test the default constants that were set."""

from file_scraper.defaults import PRONOM_DICT, VERSION_DICT


def test_complicated_constants():
    """A simple test to ensure that the two complicated constants, PRONON_DICT
    and VERSION_DICT, will have appropriate type for their value.
    """
    for constant, expected_type in ((PRONOM_DICT, tuple),
                                    (VERSION_DICT, dict)):
        for key in constant:
            assert isinstance(constant[key], expected_type)
