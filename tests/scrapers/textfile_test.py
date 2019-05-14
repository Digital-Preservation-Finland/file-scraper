"""
Test TextfileScraper, which determines whether file is a text file or not.

This module tests that:
    - Following files are correctly identified as text files and their MIME
      type, version, streams and well-formedness are determined correctly:
        - plain text with either UTF-8 or Latin-1 encoding
        - xml document
        - html document
    - Empty file, pdf and gif files are identified as not text files.
"""
import pytest

from file_scraper.textfile.textfile_scraper import TextfileScraper
from tests.common import parse_results

VALID_MSG = 'is a text file'
INVALID_MSG = 'is not a text file'


@pytest.mark.parametrize(
    ["filename", "mimetype", "is_textfile"],
    [
        ("valid__utf8.txt", "text/plain", True),
        ("valid__iso8859.txt", "text/plain", True),
        ("valid_1.0_well_formed.xml", "text/xml", True),
        ("valid_4.01.html", "text/html", True),
        ("invalid_4.01_illegal_tags.html", "text/html", True),
        ("valid_1.4.pdf", "application/pdf", False),
        ("valid_1987a.gif", "image/gif", False),
        ("invalid_1987a_broken_header.gif", "image/gif", False),
        ("invalid__empty.txt", "text/plain", False)
    ]
)
def test_existing_files(filename, mimetype, is_textfile, evaluate_scraper):
    """Test detecting whether file is a textfile."""
    correct = parse_results(filename, mimetype,
                            {}, True)
    scraper = TextfileScraper(correct.filename, True)
    scraper.scrape_file()

    correct.version = None
    correct.streams[0]['version'] = "(:unav)"
    correct.streams[0]['mimetype'] = "(:unav)"
    correct.streams[0]['stream_type'] = "(:unav)"
    correct.well_formed = is_textfile
    if correct.well_formed:
        correct.stdout_part = VALID_MSG
        correct.stderr_part = ''
        evaluate_scraper(scraper, correct)
    else:
        assert INVALID_MSG in scraper.errors()
        assert scraper.errors()
        assert not scraper.well_formed
