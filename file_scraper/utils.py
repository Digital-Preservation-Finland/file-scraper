"""Utilities for scrapers."""
from __future__ import annotations

from collections.abc import Iterator, Iterable
from pathlib import Path
from typing import TypedDict

import hashlib
import re
import zipfile
from io import BufferedReader

from file_scraper.defaults import UNAV


def hexdigest(
    filename: str | Path,
    algorithm: str = "sha1",
    extra_hash: str | bytes | None = None,
) -> str:
    """
    Calculte hash of given file.

    :param filename: File path
    :param algorithm: Hash algorithm. MD5 or SHA variant.
    :param extra_hash: Hash to be appended in calculation
    :returns: Calculated hash
    """
    algorithm = algorithm.replace("-", "").lower().strip()
    checksum = hashlib.new(algorithm)
    with open(filename, "rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            checksum.update(chunk)
        if extra_hash:
            if isinstance(extra_hash, str):
                extra_hash = extra_hash.encode("utf-8")
            checksum.update(extra_hash)
    return checksum.hexdigest()


def normalize_charset(charset: str | None) -> str:
    """
    Normalize charset to its most common and supported form.

    For example, 'US-ASCII' is converted to 'UTF-8' as it is backwards
    compatible and 'UTF-8' is more commonly recognized than 'US-ASCII'.
    :param charset: Charset
    :returns: Normalized charset in upper-case
    """
    if charset is None or charset.upper() == "BINARY":
        return UNAV
    if charset.upper() == "US-ASCII":
        return "UTF-8"
    if charset.upper() == "ISO-8859-1":
        return "ISO-8859-15"
    return charset.upper().removesuffix("LE").removesuffix("BE")


def iso8601_duration(time: float | int) -> str:
    """Convert seconds into ISO 8601 duration.

    PT[hours]H[minutes]M[seconds]S format is used with maximum of two decimal
    places used with the seconds. If there are no hours, minutes or seconds,
    that field is not included in the output, unless the total duration is
    zero, at which case "PT0S" is returned.

    >>> iso8601_duration(1.1)
    "PT1.1S"
    >>> iso8601_duration(1.001)
    "PT1S"
    >>> iso8601_duration(60)
    "PT1M"
    >>> iso8601_duration(3601)
    "PT1H1S"
    >>> iso8601_duration(0.001)
    "PT0S"

    :param time: Time in seconds
    :returns: ISO 8601 representation of time
    """
    hours = int(time // (60 * 60))
    minutes = int(time // 60 % 60)
    seconds = round(time % 60, 2)

    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1

    duration = "PT"

    if hours:
        duration += f"{hours:d}H"
    if minutes:
        duration += f"{minutes:d}M"
    if seconds > 0:
        seconds = strip_zeros(f"{seconds:.2f}")
        duration += f"{seconds}S"
    if duration == "PT":
        duration = "PT0S"

    return duration


def strip_zeros(float_str: str) -> str:
    """Recursively strip trailing zeros from a float.

    Zeros in integer part are not affected. If no decimal part is left, the
    decimal separator is also stripped. Underscores as described in PEP 515
    are allowed in the given string and stripped where the trailing digits are
    stripped, but otherwise unaffected.

    >>> strip_zeros("44.10")
    "44.1"
    >>> strip_zeros("44.0")
    "44"
    >>> strip_zeros("1_234_000.000_000")
    "1_234_000"

    :param float_str: Float number as string
    :returns: Stripped float as string
    """

    # if '.' is found in the string and string
    # ends in '0', '.' or '_' strip last character
    if float_str.find(".") != -1 and float_str[-1] in ["0", ".", "_"]:
        return strip_zeros(float_str[:-1])

    return float_str


def ensure_text(
    string: str | bytes | int, encoding: str = "utf-8", errors: str = "strict"
):
    """Coerce string to str.
    """
    # pylint: disable=invalid-name
    if isinstance(string, bytes):
        return string.decode(encoding, errors)
    if isinstance(string, str):
        return string
    if isinstance(string, int):
        return str(string)

    raise TypeError(f"not expecting type '{type(string)}'")


def concat(lines: Iterable[str], prefix: str = "") -> str:
    """
    Join given list of strings to single string separated with newlines.

    :param lines: List of string to join
    :param prefix: Prefix to prepend each line with
    :returns: Joined lines as string
    """
    return "\n".join([f"{prefix}{line}" for line in lines])


def iter_utf_bytes(
    file_handle: BufferedReader, chunksize: int, charset: str
) -> Iterator[bytes]:
    """
    Iterate given file with matching the bytes with variable length UTF
    characters. The byte sequence might have incomplete UTF characer in the
    end. This is reserved for the next chunk.

    :param file_handle: File handle to read
    :param chunksize: Size of the chunk to read
    :param charset: Character encoding of the file
    :returns: Sequence from the file
    """
    utf_buffer = b""
    chunksize += 4 - chunksize % 4  # needs to be divisible by 4

    while True:
        chunk = utf_buffer + file_handle.read(chunksize)

        if not chunk:
            return

        if charset.upper() == "UTF-8":
            chunk, utf_buffer = utf_sequence(chunk, [
                {"smallest": 0xc0, "largest": 0xdf, "indexes": [1]},
                {"smallest": 0xe0, "largest": 0xef, "indexes": [1, 2]},
                {"smallest": 0xf0, "largest": 0xf7, "indexes": [1, 2, 3]}])
        elif charset.upper() == "UTF-16":
            chunk, utf_buffer = utf_sequence(
                chunk, [{"smallest": 0xd8, "largest": 0xdb,
                         "indexes": [1, 2]}], True)

        yield chunk


class _SequenceParams(TypedDict):
    smallest: int
    largest: int
    indexes: list[int]


def utf_sequence(
    chunk: bytes,
    sequence_params: list[_SequenceParams],
    possible_le: bool = False,
) -> tuple[bytes, bytes]:
    """
    Split the given byte chunk to UTF sequence and remainder. Remainder
    is possible if last character of byte chunk is incomplete.

    :param chunk: Chunk to match
    :param sequenc_params: List of dicts of smallest and largest byte value
        of the first byte (or the second in big endian) of a character
    :param possible_le: True, little endian is possible, False otherwise
    :returns: Tuple (x, y) where x is UTF sequence and y is remainder
    """
    if len(chunk) < 4:
        return (chunk, b"")

    for params in sequence_params:

        for index in params["indexes"]:

            if len(chunk) < index:
                continue

            sequence_char = chunk[-index]
            if params["smallest"] <= sequence_char <= params["largest"]:
                if possible_le and index == 1:
                    index = index + 1  # Move index left for little endian
                return chunk[:-index], chunk[-index:]

    return (chunk, b"")


def is_zipfile(filename: Path) -> bool:
    """
    Check if file is a ZIP file.

    Ideally this would be done using zipfile.is_zipfile function. However there
    is an outstanding issue with that function and thus we can't use it
    directly.

    Relevant Github issue: https://github.com/python/cpython/issues/72680

    :param filename: File to check
    """
    if zipfile.is_zipfile(filename):
        try:
            with zipfile.ZipFile(filename):
                return True
        except (OSError, zipfile.BadZipFile):
            return False
    else:
        return False


def filter_unwanted_chars(info_string: str) -> str:
    """Filter out characters that are not compatible with XML 1.1

    Sometimes scraper output contains control characters from the scraping
    tools we use, and we want to get rid of these characters so that scraper
    output is compatible with XML.

    Restricted characters in XML 1.1 are listed here:
    https://www.w3.org/TR/xml11/#charsets

    :param info_string: String to run filtering on
    :returns: Filtered string
    """

    unwanted_chars = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                      (0x7F, 0x84), (0x86, 0x9F),
                      (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
                      (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                      (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                      (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                      (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                      (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                      (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                      (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                      (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)]

    unwanted_ranges = [fr'{chr(low)}-{chr(high)}' for (low, high) in
                       unwanted_chars]
    unwanted_chars_regex_string = '[' + ''.join(unwanted_ranges) + ']'
    unwanted_chars_re_pattern = re.compile(
        unwanted_chars_regex_string)

    return unwanted_chars_re_pattern.sub('', info_string)


def parse_exif_version(version: str) -> str:
    """
    Parse Exif version from its 4-char format into a dot-separated
    version string.

    Any strings shorter than 4 characters are right-padded with zeroes first,
    though this is against the spec and done to ensure even spec non-compliant
    values can be parsed.

    For example,

    >>> parse_exif_version("0230")
    "2.3"
    >>> parse_exif_version("0231")
    "2.3.1"
    >>> parse_exif_version("023")  # Non-compliant values are tolerated
    "2.3"
    """
    # The assumption here is that incorrect software adds
    # null-terminator when it is disallowed as noted by ExifTool
    # developers; pad zeroes as necessary.
    version = version.ljust(4, "0")

    # Per Exif spec, the two parts for major and minor version parts
    # are concatenated with any zeroes stripped beforehand
    # to produce a human-readable version number.
    # (eg. "0231" -> "2.31" and "0230" -> "2.3")
    #
    # We use "X.Y.Z" or "X.Y" pattern instead ("2.3.1" and "2.3").
    ver_a, ver_b1, ver_b2 = (
        version[0:2].strip("0"),
        version[2],
        version[3]
    )
    version_parts = [ver_a, ver_b1]
    if ver_b2 != "0":
        version_parts += [ver_b2]

    return ".".join(version_parts)
