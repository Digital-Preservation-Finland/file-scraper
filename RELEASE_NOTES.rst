Release notes
=============

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
