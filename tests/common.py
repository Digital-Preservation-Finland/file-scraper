"""Common functions for tests
"""
import os


def get_valid_files():
    """Get all valid files from tests
    :returns: dict where  key is filename and value is tuple
              (mimetype, version)
    """
    result_dict = {}
    for root, directory, filenames in os.walk('tests/data'):
        for fname in filenames:
            if fname.startswith('valid_'):
                fullname = os.path.join(root, fname)
                mimetype = root.split('/')[-1].replace("_", "/")
                if '_' in fname:
                    version = fname.rsplit('.', 1)[0].split('_')[1]
                else:
                    version = ''
                result_dict[fullname] = (mimetype, version)
    return result_dict
