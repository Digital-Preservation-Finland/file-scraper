"""Common functions for tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from file_scraper.defaults import UNAP, UNAV

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from file_scraper.scraper import Scraper, ScraperResults


def get_files(well_formed: bool) -> Iterator[tuple[str, str, str]]:
    """Get all well-formed/not well-formed files from tests.

    :param well_formed: True if well-formed file list, False for not
        well-formed.
    :returns: Generator that outputs tuple of (fullname, mimetype, version)
    """
    prefix = "valid_" if well_formed else "invalid_"
    for root, _, filenames in os.walk("tests/data"):
        for fname in filenames:
            if fname.startswith(prefix):
                fullname = os.path.join(root, fname)
                mimetype = root.split("/")[-1].replace("_", "/")
                version = os.path.splitext(fname)[0].split("_")[1]
                if not version:
                    version = UNAP
                yield fullname, mimetype, version


class Correct:
    """Class for the correct results."""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self) -> None:
        """Initialize attributes."""
        self.filename: Path | None = None
        self.purpose: str | None = None
        self.streams: dict[int, Any] = {}
        self.stdout_part: str | None = None
        self.stderr_part: str | None = None
        self.well_formed: bool | None = None
        self.params: dict[str, Any] = {}

    def update_mimetype(self, new_mimetype: str) -> None:
        """
        Changes the MIME type of the object.

        This can be needed e.g. when predefined file format is different, e.g.
        HTML document is changed to plain text.

        :param new_mimetype: New MIME type
        """
        if self.streams:
            self.streams[0]["mimetype"] = new_mimetype

    def update_version(self, new_version: str) -> None:
        """
        Changes the version of the object.

        This can be needed e.g. when predefined file format version is
        different, e.g. PDF/A-1a is changed to PDF 1.4.

        :param new_version: New file format version
        """
        if self.streams:
            self.streams[0]["version"] = new_version


def parse_results(
    filename: str,
    mimetype: str,
    results: dict[str, Any],
    check_wellformed: bool,
    params: dict[str, Any] | None = None,
    basepath: str = "tests/data",
) -> Correct:
    """
    Parse expected results from filepath and given results.

    :param filename: File name
    :param mimetype: Mimetype
    :param results: Expected results::

            {
                "purpose": <Purpose of the test>,
                "stdout_part": <Part of expected stdout>,
                "stderr_part": <Part of expected stderr>,
                "streams": <Expected streams>,
                "inverse": <True to inverse the expected well-formedness>,
            }

    :param check_wellformed: True, if well-formed check, otherwise False
    :param basepath: Base path
    :param params: Parameters for the extractor
    :returns: Correct instance, with expected results for tests
    """
    # pylint: disable=too-many-locals, too-many-arguments, too-many-branches
    well_dict = {"valid": True, "invalid": False}
    well_dict_no_check = {"valid": None, "invalid": False}
    path = os.path.join(basepath, mimetype.replace("/", "_"))
    words = os.path.splitext(filename)[0].split("_", 2)
    well_formed = words[0]
    if "streams" in results and "version" in results["streams"][0]:
        version = results["streams"][0]["version"]
    else:
        version = words[1] if len(words) > 1 and words[1] else UNAP
    testfile = os.path.join(path, filename)

    correct = Correct()
    correct.filename = Path(testfile)
    if "purpose" in results:
        correct.purpose = results["purpose"]

    if "stdout_part" in results:
        correct.stdout_part = results["stdout_part"]
    if "stderr_part" in results:
        correct.stderr_part = results["stderr_part"]

    stream_type, stream_subtype = mimetype.split("/")
    if stream_type == "application":
        stream_type = "text" if stream_subtype == "json" else "binary"

    if ("invalid" in filename) != (
        "inverse" in results and results["inverse"]
    ):
        correct_mime = UNAV
        correct_ver = UNAV
        stream_type = UNAV if stream_type != "binary" else stream_type
    else:
        correct_mime = mimetype.lower()
        correct_ver = version

    if "streams" in results:
        correct.streams = results["streams"]
        correct.streams[0]["mimetype"] = correct_mime
        correct.streams[0]["version"] = correct_ver
        for index, _ in enumerate(correct.streams):
            correct.streams[index]["index"] = index
        if "stream_type" not in correct.streams[0]:
            correct.streams[0]["stream_type"] = stream_type
    else:
        correct.streams = {
            0: {
                "mimetype": correct_mime,
                "version": correct_ver,
                "index": 0,
                "stream_type": stream_type,
            }
        }

    if check_wellformed:
        correct.well_formed = well_dict[well_formed]
        if results.get("inverse") is True:
            correct.well_formed = not correct.well_formed
    else:
        correct.well_formed = well_dict_no_check[well_formed]
        if results.get("inverse") is True:
            correct.well_formed = not correct.well_formed
            if correct.well_formed:
                correct.well_formed = None

    if params is not None:
        correct.params = params

    return correct


def partial_message_included(part: str, messages: Iterable[str]) -> bool:
    """
    Check if partial message is found as a substring in one of the strings in
    messages. If the partial message is empty, it is interpreted to be found
    in any collection of messages, even if the collection is empty.

    :param part: The substring to find in messages.
    :param messages: An iterable of strings.
    :returns: True if partial message found, False otherwise
    """
    return part == "" or any(part in message for message in messages)


def filter_unap(val: str | None) -> str | None:
    """Change `val` to `None` if it is UNAP."""
    return val if val != UNAP else None


def compare_results(scraper: Scraper, results: ScraperResults) -> None:
    """Compare scraper internal state with the return values."""
    assert str(scraper.input_path) == results.path
    assert scraper.mimetype == results.mimetype
    assert scraper.version == results.version
    assert scraper.well_formed == results.well_formed
    assert scraper.grade() == results.grade
    assert scraper.info == results.info
    assert scraper.streams == results.streams
