"""Installation script for the `file-scraper` package."""
from file_scraper import __version__

from setuptools import setup, find_packages

setup(
    name='file_scraper',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    version=__version__,
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:main']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
