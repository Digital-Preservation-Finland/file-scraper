"""Test the Warchaeology extractor module."""
# TODO: Add test detail to docstring

from pathlib import Path
from typing import Callable

import pytest
from file_scraper.warchaeology.warchaeology_extractor import (
    WarchaeologyExtractor,
)

from tests.common import parse_results, partial_message_included


@pytest.mark.parametrize(
    ["filename", "result_dict"],
    [
        (
            "valid_1.0.warc",
            {
                "purpose": "Test valid 1.0 file.",
                "stdout_part": "",
                "stderr_part": "",
            },
        ),
        (
            "valid_1.1.warc",
            {
                "purpose": "Test valid 1.1 file.",
                "stdout_part": "",
                "stderr_part": "",
            },
        ),
        (
            "valid_1.0_.warc.gz",
            {
                "purpose": "Test valid compressed 1.0 file.",
                "stdout_part": "",
                "stderr_part": ""
            }
        ),
        (
            "valid_1.1_.warc.gz",
            {
                "purpose": "Test valid compressed 1.1 file.",
                "stdout_part": "",
                "stderr_part": ""
            }
        ),
        (
            "valid_1.0_wrong_suffix.txt",
            {
                "purpose": "Test valid 1.0 file with no suffix.",
                "stdout_part": "",
                "stderr_part": "",
            },
        ),
        (
            "invalid__empty.warc",
            {
                "purpose": "Test empty warc file.",
                "stdout_part": "",
                "stderr_part": "No records found in WARC",
            },
        ),
        (
            "invalid_1.0_missing_required_field.warc",
            {
                "purpose": "Test file with missing required field.",
                "stdout_part": "",
                "stderr_part": "gowarc: missing required field: WARC-Date",
            },
        ),
        (
            "invalid_1.0_no_carriage_return.warc",
            {
                "purpose": "Test file saved with LF instead of CRLF",
                "stdout_part": "",
                "stderr_part": "missing carriage return"
            }
        ),
        (
            "invalid_1.0_missing_content.warc",
            {
                "purpose": "Test file with header but no content.",
                "stdout_part": "not a http block: EOF",
                "stderr_part": "No records found in WARC"
            }
        ),
        (
            "invalid_1.0_wrong_version.warc",
            {
                "purpose": "Test file with wrong version.",
                "stdout_part": "",
                "stderr_part": "unsupported WARC version"
            }
        ),
        (
            "invalid_1.0_too_short_content_length.warc",
            {
                "purpose": "Test file with too short content-length field.",
                "stdout_part": "",
                "stderr_part": "missing line separator at end of http headers"
            }
        )
    ],
)
def test_warchaeology_extractor(
    filename: str, result_dict: dict, evaluate_extractor: Callable
) -> None:
    """Test Warchaeology extractor."""
    correct = parse_results(filename, "application/warc", result_dict, True)
    extractor = WarchaeologyExtractor(
        filename=Path(correct.filename), mimetype="application/warc"
    )

    extractor.extract()

    if not correct.well_formed:
        assert not extractor.well_formed
        assert partial_message_included(
            correct.stdout_part, extractor.messages()
        )
        assert partial_message_included(
            correct.stderr_part, extractor.errors()
        )
    else:
        evaluate_extractor(extractor, correct)


def test_is_supported() -> None:
    """Test is_supported method."""
    mime = "application/warc"
    is_supported = WarchaeologyExtractor.is_supported
    assert is_supported(mime, "1.0")
    assert is_supported(mime, "1.1")
    assert is_supported(mime, "1.0", False)
    assert is_supported(mime, "1.1", False)

    assert not is_supported(mime, "0.17")
    assert not is_supported(mime, "0.18")
    assert not is_supported("foo", "1.1")
    assert not is_supported(mime, "foo", False)
    assert not is_supported("foo", "1.0", False)
