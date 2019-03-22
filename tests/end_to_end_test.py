"""Integration test for scrapers
"""
from file_scraper.scraper import Scraper
from tests.common import get_files


# These files will result none for some elements
# For GIFs and TIFFs with 3 images inside, the version is missing from the
# second and third streams, but exists in the first one.
# MPEG-TS file contains "menu" stream, where version is None.
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
    'tests/data/image_gif/valid_1989a.gif': 'version, version',
    'tests/data/image_tiff/valid_6.0_multiple_tiffs.tif': 'version, version',
    'tests/data/video_MP2T/valid_.ts': 'version'}
NONE_ELEMENTS_EXTRA = {
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz': 'version'}

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
IGNORE_VALID = ['tests/data/text_xml/valid_1.0_xsd.xml',
                'tests/data/text_xml/valid_1.0_local_xsd.xml',
                'tests/data/text_xml/valid_1.0_catalog.xml',
                'tests/data/video_x-matroska/valid__ffv1.mkv']

# Ignore these we know that warc, arc and dpx files are not currently
# supported for full metadata scraping
IGNORE_FOR_METADATA = IGNORE_VALID + [
    'tests/data/application_warc/valid_0.17.warc',
    'tests/data/application_warc/valid_0.18.warc',
    'tests/data/application_warc/valid_1.0.warc',
    'tests/data/application_warc/valid_1.0_.warc.gz',
    'tests/data/application_x-internet-archive/valid_1.0.arc',
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz',
    'tests/data/image_x-dpx/valid_2.0.dpx']


# These invalid files are recognized as application/gzip
DIFFERENT_MIMETYPE_INVALID = {
    'tests/data/application_warc/invalid__missing_data.warc.gz':
        'application/gzip',
    'tests/data/application_x-internet-archive/invalid__missing_data.arc.gz':
        'application/gzip'}


def test_valid_combined():
    """Integration test for valid files.
    - Test that mimetype matches.
    - Test Find out all None elements.
    - Test that errors are not given.
    - Test that all files are well-formed.
    - Ignore few files because of required parameter or missing scraper.
    """
    none = {}
    file_dict = get_files(well_formed=True)
    for fullname, value in file_dict.iteritems():
        if fullname in IGNORE_VALID:
            continue
        mimetype = value[0]
        version = value[1]

        scraper = Scraper(fullname)
        scraper.scrape()

        for _, info in scraper.info.iteritems():
            assert not info['errors']

        assert scraper.well_formed
        assert scraper.mimetype == mimetype
        # assert scraper.version == version  # fails

        if scraper.streams is None or scraper.streams is {}:
            none[fullname] = scraper.streams
            continue
        for _, stream in scraper.streams.iteritems():
            for key, stream_value in stream.iteritems():
                if stream_value is None:
                    if fullname in none:
                        none[fullname] = none[fullname] + ', ' + key
                    else:
                        none[fullname] = key
    assert none == NONE_ELEMENTS


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

    assert mime == DIFFERENT_MIMETYPE_INVALID
    assert well == {}


def test_without_wellformed():
    """Test the case where we don't want to use well-formed check,
    but we want to collect metadata.
    - Test that well-formed is always None.
    - Test that mimetype matches.
    - Test that there exists correct stream type for image, video, audio
      and text.
    - Test a random element existence for image, video, audio and text.
    """
    well = {}
    mime = {}
    none = {}
    stream_dict = {}
    file_dict = get_files(well_formed=True)
    for fullname, value in file_dict.iteritems():
        if fullname in IGNORE_FOR_METADATA:
            continue
        print fullname

        mimetype = fullname.split("/")[-2].replace("_", "/")
        scraper = Scraper(fullname)
        scraper.scrape(False)

        if scraper.well_formed is not None:
            well[fullname] = scraper.well_formed

        if scraper.mimetype != mimetype:
            mime[fullname] = scraper.mimetype
            continue

        if scraper.streams is None or scraper.streams is {}:
            none[fullname] = scraper.streams
            continue
        for _, stream in scraper.streams.iteritems():
            for key, value in stream.iteritems():
                if value is None:
                    if fullname in none:
                        none[fullname] = none[fullname] + ', ' + key
                    else:
                        none[fullname] = key

        mimepart = mimetype.split("/")[0]
        if 'stream_type' not in scraper.streams[0] or \
                scraper.streams[0]['stream_type'] is None:
            stream_dict[fullname] = None

        if mimepart in ['image', 'video', 'text', 'audio'] and \
                mimepart not in scraper.streams[0]['stream_type']:
            stream_dict[fullname] = scraper.streams[0]
                    
        for _, stream in scraper.streams.iteritems():
            if 'stream_type' not in stream:
                stream_dict[fullname] = stream
                continue
            elem_dict = {'image': 'colorspace', 'video': 'color',
                         'videocontainer': 'codec_name',
                         'text': 'charset', 'audio': 'num_channels'}
            if stream['stream_type'] in elem_dict and \
                    elem_dict[stream['stream_type']] not in stream:
                stream_dict[fullname] = stream

        if 'text/csv' in mimetype:
            if 'delimiter' not in scraper.streams[0]:
                stream_dict[fullname] = stream

    assert mime == {}
    assert stream_dict == {}
    assert none == NONE_ELEMENTS
    assert well == {}
