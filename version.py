"""
Gets the current version number.
If in a git repository, it is the current git tag.
Otherwise it is the one contained in the PKG-INFO file.

To use this script, simply import it in your setup.py file
and use the results of get_version() as your package version:

    from version import *

    setup(
        ...
        version=get_version(),
        ...
    )
"""

from __future__ import print_function

__all__ = ('get_version')

import os.path
import re
from subprocess import Popen, PIPE

VERSION_RE = re.compile('^Version: (.+)$', re.M)


def call_git_describe():
    """Determine package version from Git describe command"""
    cmd = 'git describe --abbrev --tags --match v[0-9]*'.split()
    print(' '.join(cmd))
    git = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (stdout, _) = git.communicate()
    return stdout.strip()


def write_pkg_info():
    """Write package metadata PKG-INFO file"""

    if os.path.isfile('PKG-INFO'):
        return

    project_path = os.path.abspath(os.path.dirname(__file__))

    try:
        version = re.match(
            r".*-v([\d\.]+-[^-]+-g[^/]+)",
            project_path).group(1)
    except AttributeError:
        version = '0.0'

    print("{}: Writing version info to: {}".format(
        __file__, os.path.abspath('PKG-INFO')))

    with open(os.path.join(project_path, 'PKG-INFO'), 'w') as pkginfo:

        pkginfo.write("Metadata-Version: 1.0\n")
        pkginfo.write("Name: information-package-tools\n")
        pkginfo.write("Version: %s\n" % version)
        pkginfo.write("Summary: UNKNOWN\n")
        pkginfo.write("Home-page: UNKNOWN\n")
        pkginfo.write("Author: UNKNOWN\n")
        pkginfo.write("Author-email: UNKNOWN\n")
        pkginfo.write("License: UNKNOWN\n")
        pkginfo.write("Description: UNKNOWN\n")
        pkginfo.write("Platform: UNKNOWN\n")


def get_version():
    """Determine version number for the project"""

    project_path = os.path.dirname(__file__)
    git_repo_path = os.path.join(project_path, '../../.git')

    if os.path.isdir(git_repo_path):
        # Get the version using "git describe".
        version_git = call_git_describe()

        # PEP 386 compatibility
        if version_git:
            version = "%s-%s" % (
                '.post'.join(version_git.split('-')[:2]),
                '-'.join(version_git.split('-')[2:])
            )

        print("Version number from GIT repository:", version)

    else:
        write_pkg_info()
        # Extract the version from the PKG-INFO file.
        with open(os.path.join(project_path, 'PKG-INFO')) as pkginfo:
            version = VERSION_RE.search(pkginfo.read()).group(1)
        print("Version number from PKG-INFO:", version)

    return version


if __name__ == '__main__':
    print(get_version())
