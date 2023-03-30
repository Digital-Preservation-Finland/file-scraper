Release notes
=============

Version 0.55
------------

- Python 2.7 support officially removed.

Version 0.54
------------

- Fix WMA and WMV file date rate detection.
- Changed grading according to version 1.11.0 of DPS File Formats
  specifications.
- Fix wrong script paths.
- Add missing return code handling to multiple scrapers.
- Fix color detection for specific WMV files.

Version 0.53
------------

- Add support for SIARD file format.
- Add support for WMA and WMV file formats.
- Fix issue where FFmpeg was run even though file format well-formed check was
  skipped.

Version 0.52
------------

- Add support for AIFF file format.

Version 0.51
------------

- Add support for DNG file format versions 1.1 and 1.2.

Version 0.49-0.50
-----------------

- Pin file-magic version 0.4.0 or less since newer version requires a newer
  libmagic than CentOS 7 ships by default.

Version 0.48
------------

- Make scraper functional with veraPDF older than 1.18. In older versions, ``.pdf``
  file extension is required for the PDF files.
- Fix veraPDF command similar to JHOVE command.
- Handle possible errors found in file format detection properly.
- Allow wand to deliver EXIF version as ASCII codes or plain text.

Version 0.47
------------

- Add test case for file-5.30 recursion bug

Version 0.46
------------

- Improve LxmlScraper's error handling.

Version 0.45
------------

- Fix scraper not being able to scrape PDF files that do not have ``.pdf`` file
  extension. This requires veraPDF 1.18 or newer.

Version 0.44
------------

- Update installation guide for Python 3.6 in README.rst.
- Add DNG file format support.
- Fix DV file format detection.
- Update requirements in setup file.

Version 0.43
------------

- Add MPEG-4 version 2 (ISO/IEC 14496-14) video container support.

Version 0.42
------------

- Add support for JHove 1.24.1.
- Fix bug in quicktime identification.
- Add EPUB support to file scraper.

Version 0.41
------------

- Fix bug caused by wand trying to UTF-8 decode latin-1 Exif field values.
  WandScraper will not try to handle Exif field values that it does not use.

Version 0.40
------------

- Changed grading according to version 1.10.0 of DPS File Formats
  specifications
- Changed the name ``ContainerGrader`` to a more precise
  ``ContainerStreamsGrader``
- Addeed quote character support for CSV files.

Version 0.39
------------

- Update version number in file_scraper/__init__.py

Version 0.38
------------

- Fix bug in detecting missing files when mimetype option was given

Version 0.37
------------

- Use LibreOffice 7.2 to scrape MS Office formats. This fixes stuck processes
  with certain MS Excel files.

Version 0.35-0.36
-----------------

- Minor fix in e2e tests.

Version 0.34
------------

- Changes in PDF scraping:
  - Both JHove and Ghostscript are now run for all PDF files, but the scraping
    results are ignored if the file is not supported by the tool.
  - Added PDF root version reporting to JHove scraper output
- Select Python 2/3 version of dpx-validator depending on the current
  environment.
- Added grades for files into the scraper output. The grade defines
  whether a file is recommended or suitable for digital preservation.
- Well-formed result is unknown for non-supported file or stream formats.
- MIME type is (usually) given even if there is no scraper implementation.
- Added ProRes grading as bit-level format with recommended format.
- Added video/avi support.

Version 0.33
------------

- Unknown text encodings are processed without failing
- Forbidden characters set is expanded for ISO-8859-15 charsets
- Better handling of local XML schema file paths

Version 0.32
------------

- Fix PDF version detection
- Remove ARC file format support
- Update PRONOM codes for file formats
- Handle conflicts between scraper results in a new scraper
- Update MS Office version handling

Version 0.31
------------

- Build el7 python3 rpms
- Fix scraper CLI in python3

Version 0.30
------------

- Filter out unicode normalization warnings

Version 0.29
------------

- Fix illegal control characters being printed in scraper error messages
- Minor fixes related to schema cleanup

Version 0.28
------------

- Fix accidental set-type value

Version 0.27
------------

- Build el8 rpms
- Fix Fido caching bug

Version 0.26
------------

- Support for JPEG/EXIF files with older file magic library, tested with 5.11

Version 0.25
------------

- Support validation of XML files with relative path to local schemas

Version 0.24
------------

- Increase maximum CSV field size

Version 0.23
------------

- Fix colorspace value handling and add support for ICC profile name
- Remove JPEG2000 from AVI and AVC/AAC from MPEG-1/2 PS to meet the current specifications
- Support newer version of veraPDF

Version 0.22
------------

- FLAC stream support for Matroska videos added
- MIME type update for LPCM streams
- Wand memory leaking issues fixed
- Filter unnecessary v.Nu warnings related to HTML5 validation
- Distinguish JP2 and JPX files

Version 0.21
------------

Add command-line interface

Version 0.20
------------

- Add key to info dict to contain used tools in scraping
- Minor bugfix related to unavailabe file format version

Version 0.19
------------

- Raise maximum image size for PIL
- Add support for images with grayscale+alpha channels

Version 0.18
------------

Changed Wand and ImageMagick error messages have been updated to tests.

Version 0.17
------------

Exif version is extracted from JPEG metadata using Python Wand module. JFIF version is extracted with file-scraper's magiclib module. Exif version for a JPEG file consists of four bytes of ASCII values representing eg. '0221' which is interpreted as 2.2.1, conforming to `the Finnish national digital preservation service specification for file formats`__.


__ http://digitalpreservation.fi/files/File-Formats-1.8.0.pdf
