"""Common scraper functions for tests
"""
import os.path

class Correct(object):
    """Class for the correct results
    """
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


def parse_results(filename, mimetype, results, validation):
    """Parse results from filepath and given results.
    :filename: File name
    :mimetype: Mimetype
    :results: Results: purpose, part of stdout, part of stderr,
              streams if not default, params if not empty
    :validation: True, if validation, otherwise False
    :returns: Correct instance
    """
    well_dict = {'valid': True, 'invalid': False}
    path = os.path.join('tests/data', mimetype.replace("/", "_"))
    words = filename.rsplit(".", 1)[0].split("_", 2)
    well_formed = words[0]
    if len(words) > 1:
        version = words[1]
    else:
        version = ''
    testfile = os.path.join(path, filename)

    correct = Correct()
    correct.filename = testfile
    correct.purpose = results['purpose']
    correct.mimetype = mimetype
    correct.version = version
    correct.stdout_part = results['stdout_part']
    correct.stderr_part = results['stderr_part']
    if 'streams' in results:
        correct.streams = results['streams']
    else:
        stream_type = mimetype.split('/')[0]
        if stream_type == 'application':
            stream_type = 'binary'
        correct.streams = {0: {
            'mimetype': mimetype,
            'version': version,
            'index': 0,
            'stream_type': stream_type
        }}   
    if validation:
        correct.well_formed = well_dict[well_formed]
    if 'inverse' in results and correct.well_formed is not None:
        correct.well_formed = not correct.well_formed
    if 'params' in results:
        correct.params = results['params']
    return correct
