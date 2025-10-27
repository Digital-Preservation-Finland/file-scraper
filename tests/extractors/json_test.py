"""This module tests that JSON documents get extracted correctly."""

import pytest

from tests.common import parse_results
from file_scraper.json.json_extractor import JsonExtractor
from dpres_file_formats.defaults import UnknownValue as Unk


@pytest.mark.parametrize(
    "filename",
    [
        "invalid__empty.json",
        "invalid__only_one_root_element.json",
        "invalid__property_needs_doublequotes.json",
        "invalid__single_quotes_are_not_allowed.json",
        "valid__.json",
        "valid__empty_object.json",
        "valid__ugly.json",
    ]
)
def test_json_extractor(filename):
    """
    Tests JsonExtractors extract method

    :filename: Test file name
    """
    expect_valid = True
    mimetype = "application/json"
    if "invalid_" in filename:
        expect_valid = False
    correct = parse_results(filename, mimetype, {}, False)
    extractor = JsonExtractor(filename=correct.filename,
                              mimetype=mimetype)
    extractor.extract()

    extractor.well_formed is expect_valid
    correct.streams[0]["stream_type"] = "text"
    correct.update_mimetype("application/json")
    correct.streams[0]["version"] = Unk.UNAP
