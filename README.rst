File Scraper
============

This software collects metadata and validates files.

Installation
------------

This software is tested with Python 2.7 with Centos 7.x / RHEL 7.x releases.

Install the required software with commands::

    sudo pip install virtualenv
    virtualenv .venv
    source ./.venv/bin/activate
    pip install -r requirements_dev.txt

This will install virtualenv virtual environment with the following packages, but this is NOT enough for the usage:

    * pytest, coverage, pytest-cov, Fido, file-magic, pymediainfo, ffmpeg-python, Pillow, python-wand, python-lxml, python-mimeparse

The following software is required for minimal usage without validation. The bolded software are NOT included in the pip installation script:

    * For all files: Fido, file-magic, **file-5.30**
    * Additionally, for image files: Pillow, python-wand, **ImageMagick**
    * Additionally, for audio/video files: pymediainfo, ffmpeg-python, **MediaInfo**, **FFMpeg**

Additionally, the following software is required for complete validation. The bolded software are NOT included in the pip installation script:

    * For text and xml files: python-lxml, python-mimeparse, **JHove**, **v.Nu**
    * For wave audio files: **JHove**
    * For image files: **JHove**, **dpx-validator**, **pngcheck**
    * For other files: **JHove**, **LibreOffice**, **veraPDF**, **GhostScript**, **warc-tools >= 4.8.3**, **pspp**

See also: https://github.com/Digital-Preservation-Finland/dpx-validator

Developer Usage
---------------

Use the scraper in the following way::

    from file_scraper.scraper import Scraper
    scraper = Scraper(filename)
    scraper.scrape(validation=True/False)

The ``validate`` option is True by default and does full validation for the file. To collect metadata without validation, this option must be ``False``.

As a result the collected metadata and results are in the following instance variables:

    * Path: ``scraper.filename``
    * File format: ``scraper.mimetype``
    * Format version: ``scraper.version``
    * Metadata of the streams: ``scraper.streams``
    * Detector and scraper class names, messages and errors: ``scraper.info``
    * Result of the validation: ``scraper.well_formed``

The following arguments for Scraper class are also possible:

    * For CSV validation:

        * Delimiter between elements: ``delimiter=<element delimiter>``
        * Record separator (line terminator): ``separator=<record separator>``
        * Header field names as list of strings: ``fields=[<field1>, <field2>, ...]``
        * NOTE: If these arguments are not given, the scraper tries to find out the delimiter and separator from the CSV, but may give false results.

    * For XML validation:

        * Schema: ``schema=<schema file>`` - If not given, the scraper tries to find out the schema from the XML file.
        * Use local schema catalogs: ``catalogs=True/False`` - True by default.
        * Environment for catalogs: ``catalog_path=<catalog path>``  - None by default. If None, then catalog is expected in /etc/xml/catalog
        * Disallow network use: ``no_network=True/False`` - True by default.

    * For XML Schematron validation:

        * Schematron path: ``schematron=<schematron file>`` - If is given, only Schematron scraping is executed.
        * Verbose: ``verbose=True/False`` - False by default. If False, the e.g. recurring elements are suppressed.
        * Cache: ``cache=True/False`` - True by default. The compiled files are taken from cache, if ``<schematron file>`` is not changed.
        * Hash of related abstract Schematron files: ``extra_hash=<hash>`` - ``None`` by default. The compiled XSLT files created from Schematron are cached,
          but if there exist abstract Schematron patterns in separate files, the hash of those files must be calculated and given
          to make sure that the cache is updated properly. If ``None`` then it is assumed that abstract patterns are up to date.

Additionally, the following returns a boolean value True, if the file is a text file, and False otherwise::

    scraper.is_textfile()


Copyright
---------
Copyright (C) 2019 CSC - IT Center for Science Ltd.

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
