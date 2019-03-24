#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integration test for scrapers
"""
import os
import shutil
from file_scraper.scraper import Scraper
from tests.common import get_files


# These files will result none for some elements
# For GIFs and TIFFs with 3 images inside, the version is missing from the
# second and third streams, but exists in the first one.
# MPEG-TS file contains "menu" stream, where version is None.
NONE_ELEMENTS = {
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz': ['version'],
    'tests/data/application_msword/valid_11.0.doc': ['version'],
    'tests/data/application_vnd.ms-excel/valid_11.0.xls': ['version'],
    'tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt': ['version'],
    'tests/data/application_vnd.oasis.opendocument.formula/valid_1.0'
    '.odf': ['version'],
    'tests/data/application_vnd.openxmlformats-officedocument.presentationml'
    '.presentation/valid_15.0.pptx': ['version'],
    'tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml'
    '.sheet/valid_15.0.xlsx': ['version'],
    'tests/data/application_vnd.openxmlformats-officedocument.word'
    'processingml.document/valid_15.0.docx': ['version'],
    'tests/data/image_gif/valid_1989a.gif': ['version', 'version'],
    'tests/data/image_tiff/valid_6.0_multiple_tiffs.tif': [
        'version', 'version'],
    'tests/data/video_MP2T/valid_.ts': ['version']}

# These are actually valid with another mimetype or version
# or due to special parameters or missing scraper
# invalid_1.4_wrong_version.pdf -- is valid PDF 1.7
# invalid__header_corrupted.por -- is valid text/plain
# invalid__truncated.por - is valid text/plain
# invalid_1.0_no_doctype.xhtml - is valid text/xml
# Xml files would require schema or catalog, this is tested in
# unit tests of Xmllint.
# MKV files to not have a scraper
IGNORE_INVALID = [
    'tests/data/application_pdf/invalid_1.4_wrong_version.pdf',
    'tests/data/application_x-spss-por/invalid__header_corrupted.por',
    'tests/data/application_x-spss-por/invalid__truncated.por',
    'tests/data/application_xhtml+xml/invalid_1.0_no_doctype.xhtml',
    'tests/data/video_x-matroska/invalid__ffv1_missing_data.mkv',
    'tests/data/video_x-matroska/invalid__ffv1_wrong_duration.mkv']
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
    file_dict = get_files(well_formed=True)
    for fullname, value in file_dict.iteritems():
        if fullname in IGNORE_VALID:
            continue
        mimetype = value[0]
        print fullname

        scraper = Scraper(fullname)
        scraper.scrape()

        for _, info in scraper.info.iteritems():
            assert not info['errors']

        assert scraper.well_formed
        assert scraper.mimetype == mimetype
        assert scraper.streams not in [None, {}]

        none = []
        for _, stream in scraper.streams.iteritems():
            for key, stream_value in stream.iteritems():
                if stream_value is None:
                    none.append(key)
        if fullname in NONE_ELEMENTS:
            assert none == NONE_ELEMENTS[fullname]
        else:
            assert none == []


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
    file_dict = get_files(well_formed=False)
    for fullname, _ in file_dict.iteritems():
        if 'empty' in fullname:
            continue
        if fullname in IGNORE_INVALID:
            continue
        print fullname

        mimetype = fullname.split("/")[-2].replace("_", "/")
        scraper = Scraper(fullname)
        scraper.scrape()

        skip = False
        for _, info in scraper.info.iteritems():
            if scraper.mimetype != mimetype and \
                    info['class'] == 'ScraperNotFound':
                skip = True

        if not skip:
            assert scraper.well_formed is False  # Could be also None (wrong)
            assert scraper.mimetype == mimetype or \
                fullname in DIFFERENT_MIMETYPE_INVALID


def test_without_wellformed():
    """Test the case where we don't want to use well-formed check,
    but we want to collect metadata.
    - Test that well-formed is always None.
    - Test that mimetype matches.
    - Test that there exists correct stream type for image, video, audio
      and text.
    - Test a random element existence for image, video, audio and text.
    """
    file_dict = get_files(well_formed=True)
    for fullname, _ in file_dict.iteritems():
        if fullname in IGNORE_FOR_METADATA:
            continue
        print fullname

        mimetype = fullname.split("/")[-2].replace("_", "/")
        scraper = Scraper(fullname)
        scraper.scrape(False)

        assert scraper.well_formed is None
        assert scraper.mimetype == mimetype
        assert scraper.streams not in [None, {}]
        assert 'stream_type' in scraper.streams[0]
        assert scraper.streams[0]['stream_type'] is not None

        none = []
        for _, stream in scraper.streams.iteritems():
            for key, stream_value in stream.iteritems():
                if stream_value is None:
                    none.append(key)
        if fullname in NONE_ELEMENTS:
            assert none == NONE_ELEMENTS[fullname]
        else:
            assert none == []

        mimepart = mimetype.split("/")[0]
        assert mimepart not in ['image', 'video', 'text', 'audio'] or \
            mimepart in scraper.streams[0]['stream_type']

        elem_dict = {'image': 'colorspace', 'video': 'color',
                     'videocontainer': 'codec_name',
                     'text': 'charset', 'audio': 'num_channels'}
        for _, stream in scraper.streams.iteritems():
            assert 'stream_type' in stream
            if stream['stream_type'] in elem_dict:
                assert elem_dict[stream['stream_type']] in stream

        if 'text/csv' in mimetype:
            assert 'delimiter' in scraper.streams[0]


def test_unicode_filename(testpath):
    """Integration test with unicode filename and with all scrapers.
    - Test that mimetype matches.
    - Test Find out all None elements.
    - Test that errors are not given.
    - Test that all files are well-formed.
    - Ignore few files because of required parameter or missing scraper.
    """
    file_dict = get_files(well_formed=True)
    for fullname, value in file_dict.iteritems():
        if fullname in IGNORE_VALID + [
                'tests/data/text_xml/valid_1.0_dtd.xml',
                'tests/data/application_xhtml+xml//valid_1.0.xhtml']:
            continue
        mimetype = value[0]
        if mimetype in ['application/xhtml+xml']:
            continue
        ext = fullname.rsplit(".", 1)[-1]
        unicode_name = os.path.join(testpath, u'äöå.%s' % ext)
        assert isinstance(unicode_name, unicode)

        print "Rename to unicode and scrape: %s" % fullname
        shutil.copy(fullname, unicode_name)
        scraper = Scraper(unicode_name)
        scraper.scrape()
        assert scraper.well_formed
