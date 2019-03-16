"""Installation script for the `file-scraper` package"""

from setuptools import setup, find_packages

from version import get_version

setup(
    name='file_scraper',
    packages=find_packages(exclude=['tests', 'tests.*']),
    version=get_version(),
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:main']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
