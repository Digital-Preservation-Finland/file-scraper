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
        "file-magic==0.4.0",
        "pymediainfo",
        "Pillow==6.0",
        "wand==0.6.1",
        "lxml",
        "pyexiftool==0.1",
        "ffmpeg_python@git+https://gitlab.ci.csc.fi/dpres/ffmpeg-python.git"
        "#egg=ffmpeg_python",
        "opf_fido@git+https://gitlab.ci.csc.fi/dpres/fido.git"
        "@develop#egg=opf_fido"
    ],
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:cli']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
