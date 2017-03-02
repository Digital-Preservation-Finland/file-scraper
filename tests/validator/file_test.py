"""
Tests for File (libmagick) validator.
"""

import os
import pytest
from ipt.validator.file import File


BASEPATH = "tests/data/02_filevalidation_data/"


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version'],
    [
        ("office/ODF_Text_Document.odt",
         "application/vnd.oasis.opendocument.text", "1.1"),
        ("office/ODF_Text_Document.odt",
         "application/vnd.oasis.opendocument.text", "1.2"),
        ("office/MS_Word_97-2003.doc",
         "application/msword", "11.0"),
        ("office/Office_Open_XML_Text.docx",
         "application/vnd.openxmlformats-"
         "officedocument.wordprocessingml.document", "15.0"),
        ("office/ODF_Presentation.odp",
         "application/vnd.oasis.opendocument.presentation", "1.2"),
        ("office/MS_PowerPoint_97-2003.ppt",
         "application/vnd.ms-powerpoint", "11.0"),
        ("office/Office_Open_XML_Presentation.pptx",
         "application/vnd.openxml"
         "formats-officedocument.presentationml.presentation", "15.0"),
        ("office/ODF_Spreadsheet.ods",
         "application/vnd.oasis.opendocument.spreadsheet", "1.2"),
        ("office/MS_Excel_97-2003.xls",
         "application/vnd.ms-excel", "11.0"),
        ("office/Excel_Online_Spreadsheet.xlsx",
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "15.0"),
        ("office/ODF_Drawing.odg",
         "application/vnd.oasis.opendocument.graphics", "1.2"),
        ("office/ODF_Formula.odf",
         "application/vnd.oasis.opendocument.formula", "1.2"),
        ("imagemagick/valid_dpx.dpx",
         "image/x-dpx", "2.0"),
        ("imagemagick/valid_png.png",
         "image/png", ""),
        ("imagemagick/valid_jpeg.jpeg",
         "image/jpeg", "1.01"),
        ("imagemagick/valid_jp2.jp2",
         "image/jp2", ""),
        ("imagemagick/valid_tiff.tiff",
         "image/tiff", "6.0"),
    ]
)


def test_validate_valid_file(filename, mimetype, version):

    fileinfo = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = File(fileinfo)
    validator.validate()
    assert validator.is_valid


@pytest.mark.parametrize(
    ['filename', 'mimetype', 'version'],
    [
        # Empty file
        ("office/empty_file.doc", "application/msword", "11.0"),
        # .zip renamed to .docx
        ("office/MS_Word_2007-2013_XML_zip.docx",
         "application/vnd.openxmlformats-officedocument.wordprocessingml."
         "document", "15.0"),
        # Bad xmlx created by LibreOffice
        ("office/Office_Open_XML_Spreadsheet.xlsx", "application/vnd."
         "openxmlformats-officedocument.spreadsheetml.sheet", "15.0"),
        # Wrong MIME
        ("office/ODF_Text_Document.odt", "application/msword", "11.0"),
        # .odt renamed to .doc
        ("office/ODF_Text_Document_with_wrong_filename_extension.doc",
         "application/msword", "11.0"),
    ]
)


def test_validate_invalid_file(filename, mimetype, version):

    fileinfo = {
        'filename': os.path.join(BASEPATH, filename),
        'format': {
            'mimetype': mimetype,
            'version': version
        }
    }

    validator = File(fileinfo)
    validator.validate()
    assert not validator.is_valid
