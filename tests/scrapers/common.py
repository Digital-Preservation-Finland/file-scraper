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


def iter_results(supported, results, validation):
    """Iterate results from filepath and given results.
    :supported: Suported mimetypes as list
    :results: Preferred results: purpose, part of stdout, part of stderr,
              streams if not default, params if not empty
    :validation: True, if validation, otherwise False
    :returns: Correct instance
    """
    well_dict = {'valid': True, 'invalid': False}

    for mimetype in supported:
        path = os.path.join('tests/data', mimetype.replace("/", "_"))
        filelist = os.listdir(path)
        for filename in os.listdir(path):
            if filename not in results:
                continue
            result = results[filename]
            words = filename.rsplit(".", 1)[0].split("_", 2)
            well_formed = words[0]
            version = words[1]
            testfile = os.path.join(path, filename)

            correct = Correct()
            correct.filename = testfile
            correct.purpose = result['purpose']
            correct.mimetype = mimetype
            correct.version = version
            correct.stdout_part = result['stdout_part']
            correct.stderr_part = result['stderr_part']
            if 'streams' in result:
                correct.streams = result['streams']
            else:
                correct.streams = {0: {
                    'mimetype': mimetype,
                    'version': version,
                    'index': 0,
                    'stream_type': mimetype.split('/')[0]
                }}   
            if validation:
                correct.well_formed = well_dict[well_formed]
            if 'params' in result:
                correct.params = result['params']

            yield correct
