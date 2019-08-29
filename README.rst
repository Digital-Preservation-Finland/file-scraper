File Scraper
============

This software identifies files, collects metadata from them, and checks well-formedness of a file.

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

The following software is required for minimal usage without file format well-formed check. The bolded software are NOT included in the pip installation script:

    * For all files: opf-fido, file-magic, **file-5.30**
    * Additionally, for image files: Pillow, python-wand, **ImageMagick**
    * Additionally, for audio/video files: pymediainfo, **MediaInfo**
    * Additionally, for pdf files: **veraPDF**

Additionally, the following software is required for complete well-formed check. The bolded software are NOT included in the pip installation script. Where the version supplied by the CentOS repositories differs from the one file-scraper uses, the version has been marked after the software name. It is possible that other versions work too, but file-scraper has only been tested using the marked versions.

    * For text and xml files: python-lxml, python-mimeparse, **JHove 1.20.1**, **v.Nu 17.7**, **iso-schematron-xslt1**
    * For WAVE audio files: **JHove 1.20.1**
    * For image files: **JHove 1.20.1**, **dpx-validator**, **pngcheck 2.3**
    * For audio/video files (excluding WAVE audio): ffmpeg-python, **FFMpeg 2.8.15**
    * For other files: **JHove 1.20.1**, **LibreOffice**,  **GhostScript 9.20**, **warc-tools >= 4.8.3**, **pspp 1.0.1**

See also:

    * https://github.com/Digital-Preservation-Finland/dpx-validator
    * https://github.com/Digital-Preservation-Finland/iso-schematron-xslt1
    
Where file-scraper needs to know a path to an executable or other resource, it is specified in ``file_scraper/config.py``. They correspond to the paths used by the Finnish national Digital Preservation Services, but they can be edited to match the installation locations on another system.

JHove Installation Notes
------------------------

By default, the JHove is installed to the home directory of the current user, and thus the executable is not found by the default executable search of Unix-like systems. In order for JHove to be usable by file-scraper, one of the following must be done:

* install the software in a directory included in ``$PATH`` when the installer prompts for installation location,
* add the installation location to ``$PATH``,
or

* create a symbolic link between a directory listed in ``$PATH`` and the executable, e.g. ``ln -s /home/username/jhove/jhove /usr/bin/jhove``.

Developer Usage
---------------

Use the scraper in the following way::

    from file_scraper.scraper import Scraper
    scraper = Scraper(filename)
    scraper.scrape(check_wellformed=True/False)

The ``check_wellformed`` option is ``True`` by default and does full file format well-formed check for the file. To collect metadata without checking the well-formedness of the file, this argument must be ``False``.

As a result the collected metadata and results are in the following instance variables:

    * Path: ``scraper.filename``
    * File format: ``scraper.mimetype``
    * Format version: ``scraper.version``
    * Metadata of the streams: ``scraper.streams``
    * Detector and scraper class names, messages and errors: ``scraper.info``
    * Result of the well-formed check: ``scraper.well_formed``: True: File is well-formed; False: File is not well-formed; None: The file format well-formed check was not done.

The ``scraper.streams`` includes a following kind of dict::

    {0: <stream 0>, 1: <stream 1>, ...}

where ``<stream X>`` is a dict containing the metadata elements from stream X and the key ``index``, value of which is a copy of the corresponding key in ``scraper.streams``. These streams can contain a variety of keys depending on the file type, e.g. ``height`` and ``width`` for images or ``audio_data_encoding`` for audio streams. The following keys exist in all stream metadata::

    {'mimetype': <mimetype>,         # Mimetype of the stream
     'version': <version>,           # Format version of the stream
     'index': <index>,               # Stream index
     'stream_type': <stream type>,   # Stream type: 'videocontainer', 'video', 'audio', 'image', 'text', 'binary'
     ...}                            # Other metadata keys, different keys in different stream types

The ``scraper.info`` includes a following kind of dict::

    {0: <scraper info 0>, 1: <scraper info 1>, ...}

where ``<scraper info X>`` contains name of the scraper, the resulted info messages and the resulted errors::

    {'class': <scraper name>,
     'messages': <messages from scraper>,
     'errors': <errors from scraper>}

The type of elements in the previous dictionaries is string, in exception of the ``index`` element (which is integer), and the ``messages`` and ``errors`` elements (which are lists of strings).

The following additional arguments for the Scraper are also possible:

    * For CSV file well-formed check:

        * Delimiter between elements: ``delimiter=<element delimiter>``
        * Record separator (line terminator): ``separator=<record separator>``
        * Header field names as list of strings: ``fields=[<field1>, <field2>, ...]``
        * NOTE: If these arguments are not given, the scraper tries to find out the delimiter and separator from the CSV, but may give false results.

    * For XML file well-formed check:

        * Schema: ``schema=<schema file>`` - If not given, the scraper tries to find out the schema from the XML file.
        * Use local schema catalogs: ``catalogs=True/False`` - True by default.
        * Environment for catalogs: ``catalog_path=<catalog path>``  - None by default. If None, then catalog is expected in /etc/xml/catalog
        * Disallow network use: ``no_network=True/False`` - True by default.

    * For XML Schematron well-formed check:

        * Schematron path: ``schematron=<schematron file>`` - If is given, only Schematron check is executed.
        * Verbose: ``verbose=True/False`` - False by default. If False, the e.g. recurring elements are suppressed from the output.
        * Cache: ``cache=True/False`` - True by default. The compiled files are taken from cache, if ``<schematron file>`` is not changed.
        * Hash of related abstract Schematron files: ``extra_hash=<hash>`` - ``None`` by default. The compiled XSLT files created from Schematron are cached,
          but if there exist abstract Schematron patterns in separate files, the hash of those files must be calculated and given
          to make sure that the cache is updated properly. If ``None`` then it is assumed that abstract patterns do not exists or those are up to date.
          
    * Force the scraping of a file as a specific type:
    
        * MIME type: ``mimetype=<mimetype>``. If MIME type is given, the file is scraped as this MIME type and the normal MIME type detection result is ignored. This makes it possible to e.g. scrape a file containing HTML as a plaintext file and thus not produce errors for problems like invalid HTML tags, which one might want to preserve as-is.
        * Version: ``version=<version>``. If both MIME type and version are given, the normal version detection results are also ignored, and the user-supplied version is used and reported instead. Providing a version without MIME type has no effect.

Additionally, the following returns a boolean value True, if the file is a text file, and False otherwise::

    scraper.is_textfile()

The following returns a checksum of the file with given algorithm (MD5 or SHA variant). The default algorithm is MD5::

    scraper.checksum(algorithm=<algorithm>)


File type detection without full scraping
-----------------------------------------

In some cases the full metadata information may not be of interest, and only a quick guess about the MIME type and version of the file is needed. For this, it is possible to use the ``detect_filetype()`` function in the following manner::

    from file_scraper.scraper import Scraper
    scraper = Scraper(filename)
    scraper.detect_filetype()
after which the type of the file can be addressed via ``scraper.mimetype`` and ``scraper.version``.

If full scraping has been run previously, its results are erased. ``detect_filetype`` always leaves ``scraper.streams`` as ``None`` and ``scraper.well_formed`` either as ``False`` (file could not be found or read) or ``None``. Detector information is logged in ``scraper.info`` as with normal scraping.

It should be noted that results obtained using only detectors are less accurate than ones from the full scraping, as detectors use a narrower selection of tools.


Contributing
------------

All contribution is welcome. Please see `Technical Notes <./doc/contribute.rst>`_ for more technical information about file-scraper.


Misc notes
----------

    * Without the Warctools scraper tool, gzipped WARC and ARC files are identified as 'application/gzip'.
    * With great power comes great responsibility: carelessly forcing the file type can produce unexpected results. Most files won't be reported as well-formed when the wrong MIME type is used, but in some cases where the same metadata models support both the real and the forced MIME type, the file can appear as well-formed specimen of the forced file type, possibly with wonky detected metadata. Similarly it is possible to scrape e.g. version 1987a gif as one with version 1989a, resulting in successful scraping with normal metadata apart from the forced version. Thus the results should not be blindly trusted when MIME type and/or version has been provided by the user.


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
