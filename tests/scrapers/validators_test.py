"""Test for ipt/validator/__init__.py. The purpose of this test is to make sure
that all validators are able to be found."""

from ipt.validator.validators import iter_validators
import pytest


@pytest.mark.parametrize(
    ["mimetype", "version", "charset", "validator_classes"],
    [
        ("application/x-spss-por", "", "", ["PSPP"]),
        ("application/warc", "1.0", "", ["WarctoolsWARC"]),
        ("text/csv", "", "UTF-8", ["PythonCsv", "JHoveTextUTF8"]),
        ("text/csv", "", "UTF-16", ["PythonCsv", "FileEncoding"]),
        ("text/plain", "", "ISO-8859-15", ["FileTextPlain", "FileEncoding"]),
        ("text/plain", "", "UTF-16", ["FileTextPlain", "FileEncoding"]),
        ("text/plain", "", "UTF-8", ["FileTextPlain", "JHoveTextUTF8"]),
        ("video/mpeg", "1", "", ["FFMpeg"]),
        ("video/mpeg", "2", "", ["FFMpeg"]),
        ("video/mp4", "", "", ["FFMpeg"]),
        ("application/pdf", "1.2", "", ["JHovePDF"]),
        ("application/pdf", "1.3", "", ["JHovePDF"]),
        ("application/pdf", "1.4", "", ["JHovePDF"]),
        ("application/pdf", "1.5", "", ["JHovePDF"]),
        ("application/pdf", "1.6", "", ["JHovePDF"]),
        ("application/pdf", "A-1a", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-1b", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-2a", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-2b", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-2u", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-3a", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-3b", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "A-3u", "", ["GhostScript", "VeraPDF"]),
        ("application/pdf", "1.7", "", ["GhostScript"]),
        ("image/tiff", "6.0", "", ["JHoveTiff", "File", "ImageMagick"]),
        # JHoveJPEG accepts jpeg without version number
        ("image/jpeg", "", "", ["JHoveJPEG"]),
        ("image/jpeg", "1.00", "", ["JHoveJPEG", "File", "ImageMagick"]),
        ("image/jpeg", "1.01", "", ["JHoveJPEG", "File", "ImageMagick"]),
        ("image/jpeg", "1.02", "", ["JHoveJPEG", "File", "ImageMagick"]),
        ("image/gif", "1987a", "", ["JHoveGif"]),
        ("image/gif", "1989a", "", ["JHoveGif"]),
        ("text/html", "4.01", "UTF-8", ["JHoveHTML", "JHoveTextUTF8"]),
        ("text/html", "4.01", "UTF-16", ["JHoveHTML", "FileEncoding"]),
        ("text/html", "5.0", "UTF-8", ["Vnu", "XmlEncoding", "JHoveTextUTF8"]),
        ("text/html", "5.0", "UTF-16", ["Vnu", "XmlEncoding", "FileEncoding"]),
        ("image/png", "1.2", "", ["Pngcheck", "File", "ImageMagick"]),
        ("application/warc", "0.17", "", ["WarctoolsWARC"]),
        ("application/warc", "0.18", "", ["WarctoolsWARC"]),
        ("application/warc", "1.0", "", ["WarctoolsWARC"]),
        ("application/x-internet-archive", "1.0", "", ["WarctoolsARC"]),
        ("application/x-internet-archive", "1.1", "", ["WarctoolsARC"]),
        ("text/xml", "1.0", "UTF-8",
         ["Xmllint", "XmlEncoding", "JHoveTextUTF8"]),
        ("text/xml", "1.0", "UTF-16",
         ["Xmllint", "XmlEncoding", "FileEncoding"]),
        ("application/xhtml+xml", "1.0", "UTF-8",
         ["JHoveHTML", "JHoveTextUTF8"]),
        ("application/xhtml+xml", "1.0", "UTF-16",
         ["JHoveHTML", "FileEncoding"]),
        ("application/xhtml+xml", "1.1", "UTF-8",
         ["JHoveHTML", "JHoveTextUTF8"]),
        ("application/xhtml+xml", "1.1", "UTF-16",
         ["JHoveHTML", "FileEncoding"]),
        ("text/unknown-mimetype", "1.0", "UTF-8", ["UnknownFileFormat"]),
        ("audio/x-wav", "", "", ["JHoveWAV"]),
        ("audio/x-wav", "2", "", ["JHoveWAV"]),
        # An erroneous mime type should return UnknownFileformat
        ("text/unknown-mimetype, text/unknown-mimetype", "1.0", "UTF-8",
         ["UnknownFileFormat"]),
        ("application/vnd.oasis.opendocument.text",
         "1.0", "", ["Office", "File"]),
        ("application/vnd.oasis.opendocument.text", "1.1", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.text", "1.2", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.0", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.1", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.spreadsheet", "1.2", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.presentation", "1.0", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.presentation", "1.1", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.presentation", "1.2", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.graphics", "1.0", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.graphics", "1.1", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.graphics", "1.2", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.formula", "1.0", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.formula", "1.1", "",
         ["Office", "File"]),
        ("application/vnd.oasis.opendocument.formula", "1.2", "",
         ["Office", "File"]),
        ("application/msword", "8.0", "", ["Office", "File"]),
        ("application/msword", "8.5", "", ["Office", "File"]),
        ("application/msword", "9.0", "", ["Office", "File"]),
        ("application/msword", "10.0", "", ["Office", "File"]),
        ("application/msword", "11.0", "", ["Office", "File"]),
        ("application/vnd.ms-excel", "8.0", "", ["Office", "File"]),
        ("application/vnd.ms-excel", "9.0", "", ["Office", "File"]),
        ("application/vnd.ms-excel", "10.0", "", ["Office", "File"]),
        ("application/vnd.ms-excel", "11.0", "", ["Office", "File"]),
        ("application/vnd.ms-powerpoint", "8.0", "", ["Office", "File"]),
        ("application/vnd.ms-powerpoint", "9.0", "", ["Office", "File"]),
        ("application/vnd.ms-powerpoint", "10.0", "", ["Office", "File"]),
        ("application/vnd.ms-powerpoint", "11.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "12.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "14.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "15.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "12.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "14.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "15.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "12.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "14.0", "", ["Office", "File"]),
        ("application/vnd.openxmlformats-officedocument.presentationml."
         "presentation", "15.0", "", ["Office", "File"]),
    ])
def tests_iter_validators(mimetype, version, charset, validator_classes):
    """
    Test for validator discovery.
    """
    metadata_info = {
        # "filename" must be a path that exists, otherwise NonExistingFile
        # -validator will be used
        "filename": "/dev/null",
        "format": {
            "mimetype": mimetype,
            "version": version,
            "charset": charset,
        },
        "addml": {
            "charset": charset,
            "separator": "foo",
            "delimiter": "foo",
            "header_fields": "foo"
        }
    }
    validators = iter_validators(metadata_info)
    assert set(
        [x.__class__.__name__ for x in validators]) == set(validator_classes)


def test_nonexistingfile():
    """Test that NonExistingFile validator is used if file is not found.
    """

    metadata_info = {
        "filename": "/this/path/does/not/exist",
    }
    validators = iter_validators(metadata_info)
    assert [x.__class__.__name__ for x in validators] == ["NonExistingFile"]
