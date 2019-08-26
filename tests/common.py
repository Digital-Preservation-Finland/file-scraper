"""Common functions for tests."""
from __future__ import unicode_literals

import os


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
                yield fullname, mimetype


class Correct(object):
    """Class for the correct results."""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self):
        self.filename = None
        self.purpose = None
        self.mimetype = None
        self.version = None
        self.streams = None
        self.stdout_part = None
        self.stderr_part = None
        self.well_formed = None
        self.params = {}

    def update_mimetype(self, new_mimetype):
        """
        Changes the MIME type of the object.

        This can be needed e.g. when forced file types are tested. If streams
        were found, the mimetype in the first stream is also set in addition to
        the mimetype variable.
        """
        self.mimetype = new_mimetype
        if self.streams:
            self.streams[0]["mimetype"] = new_mimetype

    def update_version(self, new_version):
        """
        Changes the version of the object.

        This can be needed e.g. when forced file types are tested. If streams
        were found, the version in the first stream is also set in addition to
        the version variable.
        """
        self.version = new_version
        if self.streams:
            self.streams[0]["version"] = new_version


def parse_results(filename, mimetype, results, check_wellformed,
                  params=None, basepath="tests/data"):
    """
    Parse results from filepath and given results.

    :filename: File name
    :mimetype: Mimetype
    :results: Results: purpose, part of stdout, part of stderr,
              streams if not default
    :check_wellformed: True, if well-formed check, otherwise False
    :basepath: Base path
    :params: Parameters for the scraper
    :returns: Correct instance
    """
    # pylint: disable=too-many-locals, too-many-arguments
    well_dict = {"valid": True, "invalid": False}
    path = os.path.join(basepath, mimetype.replace("/", "_"))
    words = filename.rsplit(".", 1)[0].split("_", 2)
    well_formed = words[0]
    version = words[1] if len(words) > 1 and words[1] else "(:unav)"
    testfile = os.path.join(path, filename)

    correct = Correct()
    correct.filename = testfile
    if "purpose" in results:
        correct.purpose = results["purpose"]

    correct.mimetype = mimetype
    correct.version = version

    if "stdout_part" in results:
        correct.stdout_part = results["stdout_part"]
    if "stderr_part" in results:
        correct.stderr_part = results["stderr_part"]

    stream_type = mimetype.split("/")[0]
    if stream_type == "application":
        stream_type = "binary"

    if "streams" in results:
        correct.streams = results["streams"]
        correct.streams[0]["mimetype"] = mimetype
        correct.streams[0]["version"] = version
        for index, _ in enumerate(correct.streams):
            correct.streams[index]["index"] = index
        if "stream_type" not in correct.streams[0]:
            correct.streams[0]["stream_type"] = stream_type
    else:
        correct.streams = {0: {
            "mimetype": mimetype,
            "version": version,
            "index": 0,
            "stream_type": stream_type
        }}

    if check_wellformed:
        correct.well_formed = well_dict[well_formed]

    if "inverse" in results and correct.well_formed is not None:
        correct.well_formed = not correct.well_formed

    if params is not None:
        correct.params = params

    return correct


def force_correct_filetype(filename, result_dict, filetype,
                           allowed_mimetypes=[]):
    """
    Create a Correct object for comparing to a scraper with forced file type.

    Initialization is done normally, but the MIME type and version are then
    updated to the expected values read from the filetype dict.

    If the MIME type was forced to a value that does not correspond to the real
    MIME type of the file and is not whitelisted by including in the
    allowed_mimetypes list, correct.well_formed is set to False. This
    corresponds to a scraper having scraped an unsupported MIME type. In this
    case, correct.streams is also set to an empty dict, meaning that if the
    object is used with evaluate_scraper() function from tests/conftest.py,
    the possibly scraped streams are not checked. If stream comparison is
    desired, either this function should not be used or the checking be done
    manually.

    :filename: Name of the file, not including the 'tests/data/mime_type/' part
    :result_dict: Result dict to be given to Correct
    :filetype: A dict containing the expected and real file types under
               the following keys:
                * expected_mimetype: the expected resulting MIME type
                * expected_version: the expected resulting version
                * correct_mimetype: the real MIME type of the file
    :allowed_mimetypes: A list of extra MIME types besides the correct_mimetype
                        that should be considered well-formed.
    """
    correct = parse_results(filename, filetype["correct_mimetype"],
                            result_dict, True)

    correct.update_mimetype(filetype["expected_mimetype"])
    correct.update_version(filetype["expected_version"])

    if (correct.mimetype != filetype["correct_mimetype"] and
            correct.mimetype not in allowed_mimetypes):
        correct.well_formed = False
        correct.streams = {}

    return correct


def partial_message_included(part, messages):
    """
    Check if partial message is found as a substring in one of the strings in
    messages. If the partial message is empty, it is interpreted to be found
    in any collection of messages, even if the collection is empty.

    :part: The substring to find in messages.
    :messages: An iterable of strings.
    """
    return part == "" or any(part in message for message in messages)
