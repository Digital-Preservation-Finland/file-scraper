"""Installation script for the `file-scraper` package."""
import re

from setuptools import setup, find_packages

with open('file_scraper/__init__.py', 'r') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='file_scraper',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    version=version,
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:main']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
