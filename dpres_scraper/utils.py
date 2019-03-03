"""Utilities for dpres-scraper"""

import os
import subprocess


def iso8601_duration(time):
    """Convert seconds into ISO 8601 duration
    PT[hours]H[minutes]M[seconds]S
    with seconds given in two decimal precision.
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
    """

    # if '.' is found in the string and string
    # ends in '0' or '.' strip last character
    if float_str.find(".") != -1 and float_str[-1] in ['0', '.']:
        return strip_zeros(float_str[:-1])

    return float_str


def combine_metadata(stream, metadata, lose=[]):
    """Merge metadata dict to stream metadata dict
    """
    if not metadata:
        return stream
    if stream is None:
        stream = {}
    for index, newitem in metadata.iteritems():
        foundkey = None
        founditem = None
        item = None
        for itemkey, item in stream.iteritems():
            if item['index'] == index:
                foundkey = itemkey
                founditem = item
                break
        if founditem is not None:
            for key, value in founditem.iteritems():
                if key in newitem and newitem[key] is not None:
                    if founditem[key] in lose:
                        founditem[key] = newitem[key]
                    elif newitem[key] not in [founditem[key]] + lose:
                        raise ValueError(
                            "Conflict with exsisting value '%s' and new "
                            "value '%s'." % (founditem[key], newitem[key]))
            for key, value in newitem.iteritems():
                if key not in founditem:
                    founditem[key] = value
            stream[foundkey] = item
        else:
            stream[index] = newitem

    return stream


def combine_element(elem1, elem2, lose=[]):
    """Merge two elements as one
    """
    if elem1 in lose:
        elem1 = elem2
    elif elem2 not in [elem1] + lose:
        raise ValueError("Conflict with exsisting value '%s' "
                         "and new value '%s'." % (elem1, elem2))
    return elem1


def run_command(cmd, stdout=subprocess.PIPE, env=None):
    """Execute command. Validator specific error handling is supported
    by forwarding exceptions.
    :param cmd: commandline command.
    :param env: Override process environment variables
    :param stdout: a file handle can be given, for directing stdout to file.
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
