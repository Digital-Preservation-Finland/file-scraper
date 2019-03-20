"""Integration test for scrapers
"""
import os

import file_scraper.scraper
from file_scraper.scraper import Scraper
from file_scraper.base import BaseScraper
from tests.common import get_files


# These files will result none for some elements
NONE_ELEMENTS = {
    'tests/data/application_msword/valid_11.0.doc': 'version',
    'tests/data/application_vnd.ms-excel/valid_11.0.xls': 'version',
    'tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt': 'version',
    'tests/data/application_vnd.oasis.opendocument.formula/valid_1.0'
    '.odf': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.presentationml'
    '.presentation/valid_15.0.pptx': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml'
    '.sheet/valid_15.0.xlsx': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.word'
    'processingml.document/valid_15.0.docx': 'version',
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz': 'version',
    'tests/data/audio_x-wav/valid__wav.wav': 'version',
    'tests/data/image_gif/valid_1989a.gif': 'version, version',
    'tests/data/image_tiff/valid_6.0_multiple_tiffs.tif': 'version, version'}


# These are actually valid with another mimetype or version
# invalid_1.4_wrong_version.pdf -- is valid PDF 1.7
# invalid__header_corrupted.por -- is valid text/plain
# invalid__truncated.por - is valid text/plain
# invalid_1.0_no_doctype.xhtml - is valid text/xml
VALID_MARKED_AS_INVALID = [
    'tests/data/application_pdf/invalid_1.4_wrong_version.pdf',
    'tests/data/application_x-spss-por/invalid__header_corrupted.por',
    'tests/data/application_x-spss-por/invalid__truncated.por',
    'tests/data/application_xhtml+xml/invalid_1.0_no_doctype.xhtml']


# These must be ignored due to special parameters or missing scraper
IGNORE = ['tests/data/text_xml/valid_1.0_xsd.xml',
          'tests/data/text_xml/valid_1.0_local_xsd.xml',
          'tests/data/text_xml/valid_1.0_catalog.xml',
          'tests/data/video_x-matroska/valid__ffv1.mkv']

# These invalid files are recognized as application/gzip
DIFFERENT_MIMETYPE = {
    'tests/data/application_warc/invalid__missing_data.warc.gz': \
        'application/gzip',
    'tests/data/application_x-internet-archive/invalid__missing_data.arc.gz': \
        'application/gzip'}


def test_valid_combined():
    """Integration test for valid files.
    - Test that mimetype matches.
    - Test Find out all None elements.
    - Test that errors are not given.
    - Test that all files are well-formed.
    - Ignore few files because of required parameter or missing scraper.
    """
    mime = {}
    ver = {}
    none = {}
    errors = {}
    well = {}
    file_dict = get_files(well_formed=True)
    for fullname, value in file_dict.iteritems():
        if fullname in IGNORE:
            continue
        mimetype = value[0]
        version = value[1]

        scraper = Scraper(fullname)
        scraper.scrape()
        print fullname

        for _, info in scraper.info.iteritems():
            if len(info['errors']) > 0:
                if fullname in errors:
                    errors[fullname] = errors[fullname] + info['errors']
                else:
                    errors[fullname] = info['errors']

        if scraper.well_formed != True:
            well[fullname] = scraper.well_formed
        if scraper.mimetype != mimetype:
            mime[fullname] = scraper.mimetype
        if scraper.mimetype != mimetype:
            ver[fullname] = scraper.version

        for _, stream in scraper.streams.iteritems():
            for key, value in stream.iteritems():
                if value is None:
                    if fullname in none:
                        none[fullname] = none[fullname] + ', ' + key
                    else:
                        none[fullname] = key
    assert mime == {}
    assert ver == {}
    assert none == NONE_ELEMENTS
    assert errors == {}
    assert well == {}


def test_invalid_combined():
    """Integration test for all invalid files.
    - Test that well_formed is False and mimetype is expected.
    - If well_formed is None, check that Scraper was not found.
    - Skip files that are known cases where it is identified
      differently (but yet correctly) than expected and would be
      well-formed.
    - Skip empty files, since those are detected as inode/x-empty
      and scraper is not found.
    """
    mime = {}
    well = {}
    file_dict = get_files(well_formed=False)
    for fullname, value in file_dict.iteritems():
        if 'empty' in fullname:
            continue
        if fullname in VALID_MARKED_AS_INVALID:
            continue
        print fullname

        mimetype = fullname.split("/")[-2].replace("_", "/")
        scraper = Scraper(fullname)
        scraper.scrape()

        scraper_found = True
        if scraper.well_formed is None:
            for _, info in scraper.info.iteritems():
                if info['class'] == 'ScraperNotFound':
                    scraper_found = False

        if scraper_found:
            if scraper.well_formed != False:
                well[fullname] = scraper.well_formed
            if scraper.mimetype != mimetype:
                mime[fullname] = scraper.mimetype 

    assert mime == DIFFERENT_MIMETYPE
    assert well == {}


class _TestScraper(BaseScraper):
    """Monkey patch for CheckTextFile class
    """
    def scrape_file(self):
        pass

    def _s_stream_type(self):
        return None

    @property
    def well_formed(self):
        if self.filename == 'textfile':
            return True
        else:
            return False


def test_is_textfile(monkeypatch):
    """Test that CheckTextFile well-formed value is returned.
    """
    monkeypatch.setattr(file_scraper.scraper, 'CheckTextFile', _TestScraper)
    scraper = Scraper('textfile')
    assert scraper.is_textfile()
    scraper = Scraper('binaryfile')
    assert not scraper.is_textfile()


def test_empty_file():
    """Test empty file.
    """
    scraper = Scraper('test/data/text_plain/invalid__empty.txt')
    scraper.scrape()
    assert not scraper.well_formed


def test_missing_file():
    """Test missing file.
    """
    scraper = Scraper('missing_file')
    scraper.scrape()
    assert not scraper.well_formed

    scraper = Scraper(None)
    scraper.scrape()
    assert not scraper.well_formed
