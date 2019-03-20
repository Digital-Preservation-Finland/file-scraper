"""Common functions for tests
"""
import os


def get_files(well_formed):
    """Get all well-formed/not well-formed files from tests
    :well_formed: True if well-formed file list, False for not well-formed.
    :returns: dict where  key is filename and value is tuple
              (mimetype, version)
    """
    if well_formed:
        prefix = 'valid_'
    else:
        prefix = 'invalid_'
    result_dict = {}
    for root, directory, filenames in os.walk('tests/data'):
        for fname in filenames:
            if fname.startswith(prefix):
                fullname = os.path.join(root, fname)
                mimetype = root.split('/')[-1].replace("_", "/")
                if '_' in fname:
                    version = fname.rsplit('.', 1)[0].split('_')[1]
                else:
                    version = ''
                result_dict[fullname] = (mimetype, version)
    return result_dict


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


def parse_results(filename, mimetype, results, validation,
                  params=None, basepath='tests/data'):
    """Parse results from filepath and given results.
    :filename: File name
    :mimetype: Mimetype
    :results: Results: purpose, part of stdout, part of stderr,
              streams if not default
    :validation: True, if validation, otherwise False
    :basepath: Base path
    :params: Parameters for the scraper
    :returns: Correct instance
    """
    well_dict = {'valid': True, 'invalid': False}
    path = os.path.join(basepath, mimetype.replace("/", "_"))
    words = filename.rsplit(".", 1)[0].split("_", 2)
    well_formed = words[0]
    if len(words) > 1:
        version = words[1]
    else:
        version = ''
    testfile = os.path.join(path, filename)

    correct = Correct()
    correct.filename = testfile
    if 'purpose' in results:
        correct.purpose = results['purpose']

    correct.mimetype = mimetype
    correct.version = version

    if 'stdout_part' in results:
        correct.stdout_part = results['stdout_part']
    if 'stderr_part' in results:
        correct.stderr_part = results['stderr_part']

    stream_type = mimetype.split('/')[0]
    if stream_type == 'application':
        stream_type = 'binary'

    if 'streams' in results:
        correct.streams = results['streams']
        correct.streams[0]['mimetype'] = mimetype
        correct.streams[0]['version'] = version
        for index, stream in enumerate(correct.streams):
            correct.streams[index]['index'] = index
        if not 'stream_type' in correct.streams[0]:
            correct.streams[0]['stream_type'] = stream_type
    else:
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

    if params is not None:
        correct.params = params

    return correct
