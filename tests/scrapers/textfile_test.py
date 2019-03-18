import pytest

from file_scraper.scrapers.textfile import CheckTextFile
from tests.scrapers.common import parse_results

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
def test_existing_files(filename, mimetype, is_textfile):
    """Test that given files are identified correctly as text files
    and not text files.
    """
    correct = parse_results(filename, mimetype,
                            {}, True)
    scraper = CheckTextFile(correct.filename, correct.mimetype, True)
    scraper.scrape_file()

    correct.version = None
    correct.streams[0]['version'] = None
    correct.streams[0]['stream_type'] = None
    correct.well_formed = is_textfile

    assert scraper.mimetype == correct.mimetype
    assert scraper.version == correct.version
    assert scraper.streams == correct.streams
    assert scraper.info['class'] == 'CheckTextFile'
    if correct.well_formed:
        assert VALID_MSG in scraper.messages()
    else:
        assert INVALID_MSG in scraper.errors()
    assert scraper.well_formed == correct.well_formed
