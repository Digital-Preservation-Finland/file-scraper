"""Installation script for the `file-scraper` package."""
from setuptools import setup, find_packages
from file_scraper import __version__

setup(
    name='file_scraper',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    version=__version__,
    install_requires=[
        "click",
        "python-mimeparse",
        "six",
        "olefile",
        "file-magic<=0.4.0;python_version == '3.6'",
        "file-magic;python_version > '3.6'",
        "pymediainfo",
        "Pillow",
        "wand",
        "lxml",
        "pyexiftool<0.5",
    ],
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:cli']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
