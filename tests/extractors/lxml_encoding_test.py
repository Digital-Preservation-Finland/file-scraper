# TODO: Rename this module
"""
Tests for lxml extractor.

This module tests that:
    - Well-formed XML files with latin-1, utf-8 or utf-16 encodings are
      reported as well_formed and the charset is identified correctly.
    - When full scraping is done, MIME type text/xml with version 1.0 and
      text/html with version 5 is reported as supported.
    - When full scraping is not done, text/xml version 1.0 is reported as not
      supported.
    - A correct MIME type with made up version is reported as supported for
      text/xml files but not for text/html files.
    - A made up MIME type with correct version is reported as not supported.
    - Extractor works as designed with charset parameter.
"""

from pathlib import Path

import pytest

from file_scraper.lxml_extractor.lxml_extractor import LxmlExtractor
from tests.common import partial_message_included


@pytest.mark.parametrize(
    (
        "header_encoding",
        "predefined_encoding",
        "expected_encoding",
    ),
    [
        # UTF-8 file
        ("UTF-8", "UTF-8", "UTF-8"),
        # Expected encoding is capitalized, even if header encoding is
        # not
        ("utf-8", "UTF-8", "UTF-8"),
        # US-ASCII is not supported in DPS, but it is compatible with
        # UTF-8
        ("US-ASCII", "UTF-8", "US-ASCII"),
        # ISO-8859-1 is not supported, but is compatible with
        # ISO-8859-15
        ("ISO-8859-1", "ISO-8859-15", "ISO-8859-1"),
    ]
)
def test_xml_header_encoding(tmpdir, header_encoding, predefined_encoding,
                             expected_encoding):
    """Test that supported encodings pass the well-formed checks.

    :param tmpdir: Temporary directory
    :param header_encoding: Encoding written to XML header
    :param predefined_encoding: The encoding that has been detected or
        predefined by the user
    :param expected_encoding: The encoding that that LxmlExtractor
        should produce
    """
    xml = f'<?xml version="1.0" encoding="{header_encoding}" ?><a>test</a>'
    tmppath = Path(tmpdir, "test.xml")
    # The actual content of file will be only ASCII characters anyway,
    # so we do not have to care about encoding when writing the file
    tmppath.write_text(xml, encoding=None)

    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        charset=predefined_encoding,
    )
    extractor.extract()

    assert extractor.well_formed is True
    assert extractor.streams[0].charset() == expected_encoding


def test_wrong_xml_header_encoding(tmpdir):
    """Test extracting files with wrong encoding in XML header.

    Creates a test file with wrong encoding in header. Error should be
    produced, and file should not be well-formed.
    """
    # ISO-8859-15 encoding in header
    xml = '<?xml version="1.0" encoding="ISO-8859-15" ?><a>test</a>'
    tmppath = Path(tmpdir, "test.xml")
    tmppath.write_text(xml)

    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        # The file has been predefined as UTF-8, which conflicts with
        # the XML header
        charset="UTF-8",
    )
    extractor.extract()

    assert extractor.well_formed is False
    assert len(extractor.errors()) == 1
    assert extractor.errors()[0].startswith(
        "Found encoding declaration ISO-8859-15"
    )
    assert extractor.errors()[0].endswith(
        "which is not compatible with UTF-8"
    )


def test_unsupported_xml_header_encoding(tmpdir):
    """Test extracting XML file with unsupported encoding in header."""
    xml = '<?xml version="1.0" encoding="this-is-not-supported" ?><a>test</a>'
    tmppath = Path(tmpdir, "test.xml")
    tmppath.write_text(xml)

    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        charset="UTF-8",
    )
    extractor.extract()

    assert extractor.well_formed is False
    # This error message is slightly different in depending on lxml
    # version:
    # 4.6.5: Unsupported encoding this-is-not-supported
    # 6.0.2: Unsupported encoding: this-is-not-supported
    assert "Unsupported encoding" in extractor.errors()[0]
    assert "this-is-not-supported" in extractor.errors()[0]
    assert not extractor.streams


def test_invalid_bytes(tmpdir):
    """Test extracting XML file with invalid encoding.

    Creates a test file where the encoding in header does not match the
    actual encoding of the file. Extractor should not not crash.
    """
    # Create a UTF-8 file with ISO-8859-15 encoding declared in XML
    # header
    xml = '<?xml version="1.0" encoding="ISO-8859-15" ?><a>ääää</a>'
    tmppath = Path(tmpdir, "test.xml")
    tmppath.write_text(xml, encoding="UTF-8")

    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        charset="UTF-8",
    )
    extractor.extract()

    assert extractor.well_formed is False
    assert extractor.errors()[0].startswith(
        "Found encoding declaration ISO-8859-15"
    )
    assert extractor.errors()[0].endswith("not compatible with UTF-8")


def test_invalid_bytes_ascii(tmpdir):
    """Test extracting UTF-8 file with ASCII encoding declared in header.

    The file is technically invalid, but LxmlExtractor omits error,
    because ASCII is compatible with UTF-8. However, XmllintExtractor
    extractor reports the file as invalid. So maybe the file should not
    be well-formed.
    """
    # Create a UTF-8 file with some other encoding declared in XML
    # header
    xml = '<?xml version="1.0" encoding="US-ASCII" ?><a>ääää</a>'
    tmppath = Path(tmpdir, "test.xml")
    tmppath.write_text(xml, encoding="UTF-8")

    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        charset="UTF-8",
    )
    extractor.extract()

    assert extractor.well_formed is True
    assert extractor.streams[0].charset() == "US-ASCII"


def test_file_format_not_supported_by_model(tmpdir):
    """Test extracting file that is not supported by metadata models.

    Because the default implementation of is_supported method
    is overwritten in LxmlExtractor, it supports file formats that are
    not supported by any metadata model (for example text/xml version
    foo). For those file formats, the extractor does not produce any
    streams, which leads to error, i.e. the files are always not
    well-formed.

    This functionality might not be desired, so this test was added to
    demonstrate how the extractor currently works.
    """
    xml = '<?xml version="1.0" encoding="UTF-8" ?><a>test</a>'
    tmppath = Path(tmpdir, "test.xml")
    tmppath.write_text(xml, encoding="UTF-8")

    assert LxmlExtractor.is_supported(mimetype="text/xml", version="foo")
    extractor = LxmlExtractor(
        filename=tmppath,
        mimetype="text/xml",
        version="foo",
        charset="UTF-8",
    )
    extractor.extract()

    assert extractor.well_formed is False
    assert not extractor.streams
    assert extractor.errors()[0] \
        == "Extractor didn't produce any output streams."


def test_is_supported_allow():
    """Test is_supported method for xml 1.0 files."""
    mime = "text/xml"
    ver = "1.0"
    assert LxmlExtractor.is_supported(mime, ver, True)
    assert LxmlExtractor.is_supported(mime, None, True)
    assert not LxmlExtractor.is_supported(mime, ver, False)
    assert LxmlExtractor.is_supported(mime, "foo", True)
    assert not LxmlExtractor.is_supported("foo", ver, True)


def test_is_supported_deny():
    """Test is_supported method for html 5 files."""
    mime = "text/html"
    ver = "5"
    assert LxmlExtractor.is_supported(mime, ver, True)
    assert LxmlExtractor.is_supported(mime, None, True)
    assert not LxmlExtractor.is_supported(mime, ver, False)
    assert not LxmlExtractor.is_supported(mime, "foo", True)
    assert not LxmlExtractor.is_supported("foo", ver, True)


@pytest.mark.parametrize(
    ("filename", "mimetype", "charset", "well_formed"),
    [
        ("tests/data/text_xml/valid_1.0_xsd.xml", "text/xml", "UTF-8", True),
        ("tests/data/text_xml/valid_1.0_xsd.xml", "text/xml", "ISO-8859-15",
         False),
        ("tests/data/text_html/valid_5.html", "text/html", "UTF-8", True),
        ("tests/data/text_html/valid_5.html", "text/html", "ISO-8859-15",
         False),
    ]
)
def test_charset(filename, mimetype, charset, well_formed):
    """Test extracting files without encoding defined in header.

    When encoding is not found in header, the default assumption of lxml
    is UTF-8. Therefore, if user defines the encoding of the file as
    ISO-8859-15, LxmlExtractor will disagree, and the file is not well
    formed, although the file really is valid ISO-8859-15 file. The
    problem has low impact, so it is probably not worth fixing.

    :param filename: Test file name
    :param mimetype: File MIME type
    :param charset: File character encoding
    :param well_formed: Expected result of well-formedness
    """
    extractor = LxmlExtractor(
        filename=Path(filename),
        mimetype=mimetype,
        charset=charset,
    )
    extractor.extract()
    assert extractor.well_formed == well_formed
    if well_formed:
        assert not extractor.errors()
    else:
        assert partial_message_included(
            "Found encoding declaration UTF-8", extractor.errors()
        )


def test_predefined_charset_unav():
    """Test scraping when charset has not been predefined."""
    extractor = LxmlExtractor(
        filename=Path("tests/data/text_xml/valid_1.0_xsd.xml"),
        mimetype="text/xml",
        charset=None,
    )
    extractor.extract()
    assert extractor.well_formed is False
    assert extractor.errors() == ["Character encoding not defined."]


@pytest.mark.parametrize("tool", ["lxml", "libxml2"])
def test_tools(tool):
    """Test that the versions are numeric"""
    extractor = LxmlExtractor(
        filename=Path("tests/data/text_xml/valid_1.0_xsd.xml"),
        mimetype="text/xml",
        charset="UTF-8",
    )
    assert extractor.tools()[tool]["version"].replace(".", "").isnumeric()
