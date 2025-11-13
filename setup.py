"""Installation script for the `file-scraper` package."""
from setuptools import setup, find_packages

setup(
    name='file_scraper',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        "click",
        "python-mimeparse",
        "olefile",
        "file-magic<=0.4.0;python_version < '3.7'",
        "file-magic;python_version >= '3.7'",
        "pymediainfo",
        "Pillow==6.0;python_version < '3.7'",
        "Pillow; python_version >= '3.7'",
        "wand==0.6.1;python_version < '3.7'",
        "wand;python_version >= '3.7'",
        "pymediainfo",
        "lxml",
        "pyexiftool",
        "jpylyzer >= 2.2.0"
    ],
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "write_to": "file_scraper/_version.py"
    },
    entry_points={'console_scripts': [
        'scraper=file_scraper.cmdline:cli']},
    zip_safe=False,
    tests_require=['pytest'],
    test_suite='tests')
