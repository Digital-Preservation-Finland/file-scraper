File Scraper
============

This software identifies files, collects metadata from them, and checks well-formedness of a file.

Requirements
------------

Installation and usage requires Python 3.9 or newer.
The software is tested with Python 3.9 on AlmaLinux 9 release.

Installation using RPM packages (preferred)
-------------------------------------------

Installation on Linux distributions is done by using the RPM Package Manager.
See how to `configure the PAS-jakelu RPM repositories`_ to setup necessary software sources.

.. _configure the PAS-jakelu RPM repositories: https://www.digitalpreservation.fi/user_guide/installation_of_tools 

After the repository has been added, the package can be installed by running one of the following commands.

For a full installation containing all validation tools::

    sudo dnf install python3-file-scraper-full

For a lighter installation containing only the core tools needed for file format identification (file format validation not supported)::

    sudo dnf install python3-file-scraper-core

Installation using Python Virtualenv for development purposes
-------------------------------------------------------------

Create a virtual environment::

    python3 -m venv venv

Run the following to activate the virtual environment::

    source venv/bin/activate

Install the required software with commands::

    pip install --upgrade pip==20.2.4 setuptools
    pip install -r requirements_github.txt
    pip install .

To deactivate the virtual environment, run ``deactivate``. To reactivate it, run the ``source`` command above.

Installing this software will install virtualenv virtual environment with the following packages, but this is NOT enough for the usage:

    * pytest, coverage, pytest-cov, Fido, file-magic, pymediainfo, ffmpeg-python, Pillow, python-wand, python-lxml, python-mimeparse, pyexiftool

The following software is required for minimal usage without file format well-formed check. Supported versions of the software is mentioned for some packages. The bolded software are NOT included in the pip installation script:

    * For all files: opf-fido 1.4.0 (patched by dpres), file-magic, **file-5.30**
    * Additionally, for image files: Pillow 6.0, python-wand 0.6.1, pyexiftool, **ImageMagick 6.9.10.68**, **ExifTool**, **ufraw**
    * Additionally, for audio/video files: pymediainfo, ffmpeg-python 0.1.16-2 (patched by dpres), **MediaInfo**, **FFMpeg 3.3.6**
    * Additionally, for pdf files: **veraPDF 1.24**

Additionally, the following software is required for complete well-formed check. The bolded software are NOT included in the pip installation script. Where the version supplied by the CentOS repositories differs from the one file-scraper uses, the version has been marked after the software name. It is possible that other versions work too, but file-scraper has only been tested using the marked versions.

    * For text and xml files: python-lxml, python-mimeparse, **JHove 1.24.1**, **v.Nu 17.7**, **iso-schematron-xslt1**
    * For image files: **JHove 1.24.1**, **dpx-validator**, **pngcheck 2.3**
    * For audio/video files: **JHove 1.24.1** (for WAVE audio files)
    * For other files: **JHove 1.24.1**, **LibreOffice 7.2**,  **GhostScript 9.20**, **warc-tools >= 4.8.3**, **pspp 1.2.0-2** (patched by dpres), **dbptk-developer >= 2.10.3**

See also:

    * https://github.com/Digital-Preservation-Finland/dpx-validator
    * https://github.com/Digital-Preservation-Finland/iso-schematron-xslt1

File-scraper uses default paths for necessary executables and other resources.
These paths can be changed by editing the configuration file
``/etc/file-scraper/file-scraper.conf``. It is also possible to use another
configuration file by setting the environment variable ``FILE_SCRAPER_CONFIG``.

JHove and veraPDF Installation Notes
------------------------------------

By default, the JHove/veraPDF is installed to the home directory of the current user, and thus the executable is not found by the default executable search of Unix-like systems. In order for JHove/veraPDF to be usable by file-scraper, one of the following must be done:

* install the software in a directory included in ``$PATH`` when the installer prompts for installation location,
* add the installation location to ``$PATH``,
or

* create a symbolic link between a directory listed in ``$PATH`` and the executable, e.g. ``ln -s /home/username/jhove/jhove /usr/bin/jhove`` and ``ln -s /home/username/verapdf/verapdf /usr/bin/verapdf``.

DBPTK-Developer installation notes
----------------------------------

By default, there is no DBPTK-Developer tool installation package. Installation
requires download from https://github.com/keeps/dbptk-developer/releases and
setting up the correct executable file.

* Download JAR file from https://github.com/keeps/dbptk-developer/releases
* Place downloaded JAR file to desired ``$PATH`` (ie */home/username/dbptk/dbptk-app-2.10.3.jar*)
* Create an executable **dbptk** (ie */home/username/dbptk/dbptk*) with following content::

    #!/bin/sh
    DBPTK_JAR_PATH="/home/username/dbptk/dbptk-app-2.10.3.jar"
    exec java -jar "$DBPTK_JAR_PATH" "$@"

* Create a symbolic link for the executable ``ln -s /home/username/dbptk/dbptk /usr/bin/dbptk``

Wand Usage Notes
----------------

Wand usage on PNG, JPEG, JP2, GIF and TIFF file formats require respective decode delegates on ImageMagick. Tests require Wand error messages as generated with ImageMagick version 6.9.10.68.

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
    * Detector and scraper class names, used software, messages and errors: ``scraper.info``
    * Result of the well-formed check: ``scraper.well_formed``: True: File is well-formed; False: File is not well-formed; None: The file format well-formed check was not done or the file/stream format is not supported.

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

where ``<scraper info X>`` contains name of the scraper, used software, the resulted info messages and the resulted errors::

    {'class': <scraper name>,
     'messages': <messages from scraper>,
     'errors': <errors from scraper>,
     'tools': <names and versions of used 3rd party software by scraper>}

The type of elements in the previous dictionaries is string, in exception of the ``index`` element (which is integer), and the ``messages``, ``errors`` and ``tools`` elements (which are lists of strings).

The following additional arguments for the Scraper are also possible:

    * For CSV file well-formed check:

        * Delimiter between elements: ``delimiter=<element delimiter>``
        * Record separator (line terminator): ``separator=<record separator>``
        * Quote character: ``quotechar=<quote character>``
        * Header field names as list of strings: ``fields=[<field1>, <field2>, ...]``
        * NOTE: If these arguments are not given, the scraper tries to find out the delimiter and separator from the CSV, but may give false results.
        * NOTE: See giving MIME type and character encoding below. CSV files are typically detected as text/plain by default.

    * For XML file well-formed check:

        * Schema: ``schema=<schema file>`` - If not given, the scraper tries to find out the schema from the XML file.
        * Use local schema catalogs: ``catalogs=True/False`` - True by default.
        * Environment for catalogs: ``catalog_path=<catalog path>``  - None by default. If None, then catalog is expected in /etc/xml/catalog
        * Disallow network use: ``no_network=True/False`` - True by default.
        * See giving the character encoding below.

    * For XML Schematron well-formed check:

        * Schematron path: ``schematron=<schematron file>`` - If is given, only Schematron check is executed.
        * Verbose: ``verbose=True/False`` - False by default. If False, the e.g. recurring elements are suppressed from the output.
        * Cache: ``cache=True/False`` - True by default. The compiled files are taken from cache, if ``<schematron file>`` is not changed.
        * Hash of related abstract Schematron files: ``extra_hash=<hash>`` - ``None`` by default. The compiled XSLT files created from Schematron are cached,
          but if there exist abstract Schematron patterns in separate files, the hash of those files must be calculated and given
          to make sure that the cache is updated properly. If ``None`` then it is assumed that abstract patterns do not exists or those are up to date.
        * See giving the character encoding below.

    * Give a specific type for scraping of a file:

        * MIME type: ``mimetype=<mimetype>``. If MIME type is given, the file is scraped as this MIME type and the normal MIME type detection result is ignored. This makes it possible to e.g. scrape a file containing HTML as a plaintext file and thus not produce errors for problems like invalid HTML tags, which one might want to preserve as-is.
        * Version: ``version=<version>``. If both MIME type and version are given, the normal version detection results are also ignored, and the user-supplied version is used and reported instead. Providing a version without MIME type has no effect.
        * Character encoding: ``charset=<charset>``. If the file is a text file, the file is validated using the given character encoding. Supported values are ``UTF-8``, ``UTF-16``, ``UTF-32`` and ``ISO-8859-15``. By default, the character encoding is detected. The detection is always a statistics-based evaluation and therefore it may sometimes give false results.

File scraper can grade the file to determine how suitable it is for digital preservation.
Possible values include ``fi-dpres-recommended-file-format``, ``fi-dpres-acceptable-file-format``, ``fi-dpres-bit-level-file-format-with-recommended``, ``fi-dpres-bit-level-file-format`` and ``fi-dpres-unacceptable-file-format``::

    scraper.grade()

Additionally, the following returns a boolean value True, if the file is a text file, and False otherwise::

    scraper.is_textfile()

The following returns a checksum of the file with given algorithm (MD5 or SHA variant). The default algorithm is MD5::

    scraper.checksum(algorithm=<algorithm>)


Command line tool
-----------------

The file scraper has a command line tool for scraping individual files. After installing the file-scraper package, it can be used with::

    scraper scrape-file [OPTIONS] FILENAME [EXTRA PARAMETERS]

The options that can be given to the tool are:

    * Skip well-formedness check: ``--skip-wellformed-check``. Don't check the file well-formedness, only scrape metadata.
    * Print tool info: ``--tool-info``. Include errors and messages from different 3rd party tools that were used.
    * Specify MIME type: ``--mimetype=<mimetype>``
    * Specify version: ``--version=<version>``

In addition to these specific options, the user can provide any extra options that will then be passed onto the scraper. These options must be in the long form, e.g. ``--charset=UTF-8`` or ``--charset UTF-8``. Only string and boolean values are currently accepted.

The tool will always print out detector/scraper errors if there are any.


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

    * Gzipped WARC files are scraped correctly only when ``check_wellformed`` parameter is ``True``.
    * Metadata is not collected for DPX images, only well-formedness is checked.
    * Retrieving version number can not be done for ODF Formula formats.
    * Scraping XML files without XML header works correctly only when ``check_wellformed`` parameter is ``True``.
    * Only audio and video stream metadata is collected for audio and video files. Other streams, such as menus and subtitles, are omitted.
    * The software may result arbitrary metadata values, if incorrect MIME type or version is given as a parameter. However, the file is also then denoted as invalid.
    * Scraping EPUB files only works when ``check_wellformed`` parameter is ``True``.

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
