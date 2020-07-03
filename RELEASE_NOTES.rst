Release notes
=============

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
