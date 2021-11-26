"""Common functions for tests."""
from __future__ import unicode_literals

import os

from file_scraper.defaults import UNAP, UNAV


def get_files(well_formed):
    """Get all well-formed/not well-formed files from tests.

    :well_formed: True if well-formed file list, False for not well-formed.
    :returns: Generator that outputs tuple of (fullname, mimetype, version)
    """
    if well_formed:
        prefix = "valid_"
    else:
        prefix = "invalid_"
    for root, _, filenames in os.walk("tests/data"):
        for fname in filenames:
            if fname.startswith(prefix):
                fullname = os.path.join(root, fname)
                mimetype = root.split("/")[-1].replace("_", "/")
                version = os.path.splitext(fname)[0].split("_")[1]
                if not version:
                    version = UNAP
                yield fullname, mimetype, version


class Correct(object):
    """Class for the correct results."""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self):
        """Initialize attributes."""
        self.filename = None
        self.purpose = None
        self.streams = None
        self.stdout_part = None
        self.stderr_part = None
        self.well_formed = None
        self.params = {}

    def update_mimetype(self, new_mimetype):
        """
        Changes the MIME type of the object.

        This can be needed e.g. when predefined file format is different, e.g.
        HTML document is changed to plain text.

        :new_mimetype: New MIME type
        """
        if self.streams:
            self.streams[0]["mimetype"] = new_mimetype

    def update_version(self, new_version):
        """
        Changes the version of the object.

        This can be needed e.g. when predefined file format version is
        different, e.g. PDF/A-1a is changed to PDF 1.4.

        :new_version: New file format version
        """
        if self.streams:
            self.streams[0]["version"] = new_version


def parse_results(filename, mimetype, results, check_wellformed,
                  params=None, basepath="tests/data"):
    """
    Parse expected results from filepath and given results.

    :filename: File name
    :mimetype: Mimetype
    :results: Expected results:
              purpose: Purpose of the test
              stdout_part: Part of expected stdout
              stderr_part: Part of expected stderr,
              streams: Expected streams
              inverse: True to inverse the expected well-formedness
    :check_wellformed: True, if well-formed check, otherwise False
    :basepath: Base path
    :params: Parameters for the scraper
    :returns: Correct instance, with expected results for tests
    """
    # pylint: disable=too-many-locals, too-many-arguments, too-many-branches
    well_dict = {"valid": True, "invalid": False}
    well_dict_no_check = {"valid": None, "invalid": False}
    path = os.path.join(basepath, mimetype.replace("/", "_"))
    words = filename.rsplit(".", 1)[0].split("_", 2)
    well_formed = words[0]
    if "streams" in results and "version" in results["streams"][0]:
        version = results["streams"][0]["version"]
    else:
        version = words[1] if len(words) > 1 and words[1] else UNAP
    testfile = os.path.join(path, filename)

    correct = Correct()
    correct.filename = testfile
    if "purpose" in results:
        correct.purpose = results["purpose"]

    if "stdout_part" in results:
        correct.stdout_part = results["stdout_part"]
    if "stderr_part" in results:
        correct.stderr_part = results["stderr_part"]

    stream_type = mimetype.split("/")[0]
    if stream_type == "application":
        stream_type = "binary"

    if ("invalid" in filename) != ("inverse" in results and
                                   results["inverse"]):
        correct_mime = UNAV
        correct_ver = UNAV
        stream_type = UNAV if stream_type != "binary" else stream_type
    else:
        correct_mime = mimetype
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
        correct.streams = {0: {
            "mimetype": correct_mime,
            "version": correct_ver,
            "index": 0,
            "stream_type": stream_type
        }}

    if check_wellformed:
        correct.well_formed = well_dict[well_formed]
    else:
        correct.well_formed = well_dict_no_check[well_formed]

    if "inverse" in results and correct.well_formed is not None:
        correct.well_formed = not correct.well_formed

    if params is not None:
        correct.params = params

    return correct


def partial_message_included(part, messages):
    """
    Check if partial message is found as a substring in one of the strings in
    messages. If the partial message is empty, it is interpreted to be found
    in any collection of messages, even if the collection is empty.

    :part: The substring to find in messages.
    :messages: An iterable of strings.
    :returns: True if partial message found, False otherwise
    """
    return part == "" or any(part in message for message in messages)
