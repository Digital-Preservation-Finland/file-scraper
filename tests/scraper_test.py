"""
"""
import os
from pprint import pprint
from file_scraper.scraper import Scraper

NONE_ELEMENTS = {
    'tests/data/application_msword/valid_11.0.doc': 'version',
    'tests/data/application_vnd.ms-excel/valid_11.0.xls': 'version',
    'tests/data/application_vnd.ms-powerpoint/valid_11.0.ppt': 'version',
    'tests/data/application_vnd.oasis.opendocument.formula/valid_1.0.odf': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.presentationml.presentation/valid_15.0.pptx': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.spreadsheetml.sheet/valid_15.0.xlsx': 'version',
    'tests/data/application_vnd.openxmlformats-officedocument.wordprocessingml.document/valid_15.0.docx': 'version',
    'tests/data/application_x-internet-archive/valid_1.0_.arc.gz': 'version',
    'tests/data/audio_x-wav/valid__wav.wav': 'version',
    'tests/data/image_gif/valid_1989a.gif': 'version, version',
    'tests/data/video_x-matroska/valid__ffv1.mkv': 'stream_type'}

def test_valid_combined():
    """
    """
    mime = {}
    ver = {}
    none = {}
    errors = {}
    well = {}
    for root, directory, filenames in os.walk('tests/data'):
        for fname in filenames:
            if fname.startswith('valid_'):
                fullname = os.path.join(root, fname)
                mimetype = root.split('/')[-1].replace("_", "/")
                if '_' in fname:
                    version = fname.rsplit('.', 1)[0].split('_')[1]
                else:
                    version = ''
                scraper = Scraper(fullname)
                scraper.scrape()
                for _, info in scraper.info.iteritems():
                    if len(info['errors']) > 0:
                        if fullname in errors:
                            errors[fullname] = errors[fullname] + info['errors']
                        else:
                            errors[fullname] = info['errors']
                print "%s %s %s" % (fname, scraper.mimetype, scraper.version)
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
    pprint(mime)
    pprint(ver)
    pprint(none)
    pprint(errors)
    pprint(well)
    assert mime == {}
    assert ver == {}
    assert none == NONE_ELEMENTS
    assert errors == {}
    assert well == {'tests/data/video_x-matroska/valid__ffv1.mkv': None}
