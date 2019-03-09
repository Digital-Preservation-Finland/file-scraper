"""Utilities for scrapers"""

import os
import subprocess
import unicodedata
import string
import hashlib


def hexdigest(filename, extra_hash=None):
    """Calculte hash of given file.
    :filename: File path
    :extra_hash: Hash to be appended in calculation
    :returns: Calculated hash
    """
    checksum = hashlib.new('sha1')
    with open(filename, 'rb') as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b''):
            checksum.update(chunk)
        if extra_hash:
            checksum.update(extra_hash)
    return checksum.hexdigest()


def sanitize_string(dirty_string):
    """Strip non-printable control characters from unicode string
    :dirty_string: String to sanitize
    :returns: Sanitized string
    """
    sanitized_string = "".join(
        char for char in dirty_string if unicodedata.category(char)[0] != "C"
        or char in string.printable)
    return sanitized_string


def iso8601_duration(time):
    """Convert seconds into ISO 8601 duration
    PT[hours]H[minutes]M[seconds]S
    with seconds given in two decimal precision.
    :time: Time in seconds
    :returns: ISO 8601 representation of time
    """
    hours = time // (60*60)
    minutes = time // 60 % 60
    seconds = time % 60

    duration = "PT"

    if hours:
        duration += "%dH" % hours
    if minutes:
        duration += "%dM" % minutes
    if seconds:
        seconds = strip_zeros("%.2f" % seconds)
        duration += "%sS" % seconds
    if duration == 'PT':
        duration = 'PT0S'

    return duration


def strip_zeros(float_str):
    """Recursively strip trailing zeros from a float i.e. strip_zeros("44.10")
    returns "44.1" and _srip_zeros("44.0") returns "44"
    :float_str: Float number as string
    :returns: Stripped float as string
    """

    # if '.' is found in the string and string
    # ends in '0' or '.' strip last character
    if float_str.find(".") != -1 and float_str[-1] in ['0', '.']:
        return strip_zeros(float_str[:-1])

    return float_str


def combine_metadata(stream, metadata, lose=[], important=None):
    """Merge metadata dict to stream metadata dict. Will raise
    ValueError if two equal and different values collide.
    :stream: Metadata dict where the new metadata is merged.
    :metadata: New metadata dict to be merged.
    :lose: These are generic values that are allowed to be lost
    :important: Important values as dict, which will be used
                in conflict situation, if given.
    :returns: Merged metadta
    """
    if not metadata:
        return stream
    if stream is None:
        stream = {}
    if important is None:
        important = {}

    for index, newitem in metadata.iteritems():

        foundkey = None
        founditem = None
        item = None
        for itemkey, item in stream.iteritems():
            if item['index'] == index:
                foundkey = itemkey
                founditem = item
                break

        if founditem is None:
            stream[index] = newitem
            continue

        for key, value in founditem.iteritems():
            if key in newitem and newitem[key] is not None:
                if founditem[key] in lose:
                    founditem[key] = newitem[key]
                elif key in important and \
                        important[key] not in lose:
                    founditem[key] = important[key]
                elif newitem[key] not in [founditem[key]] + lose:
                    raise ValueError(
                        "Conflict with exsisting value '%s' and new "
                        "value '%s'." % (founditem[key], newitem[key]))
        for key, value in newitem.iteritems():
            if key not in founditem:
                founditem[key] = value
        stream[foundkey] = item

    return stream


def run_command(cmd, stdout=subprocess.PIPE, env=None):
    """Execute command. Scraper specific error handling is supported
    by forwarding exceptions.
    :param cmd: commandline command.
    :param stdout: a file handle can be given, for directing stdout to file.
    :param env: Override process environment variables
    :returns: Tuple (statuscode, stdout, stderr)
    """
    _env = os.environ.copy()

    if env:
        for key, value in env.iteritems():
            _env[key] = value

    proc = subprocess.Popen(cmd,
                            stdout=stdout,
                            stderr=subprocess.PIPE,
                            shell=False,
                            env=_env)

    (stdout_result, stderr_result) = proc.communicate()
    if not stdout_result:
        stdout_result = ""
    if not stderr_result:
        stderr_result = ""
    statuscode = proc.returncode
    return statuscode, stdout_result, stderr_result
