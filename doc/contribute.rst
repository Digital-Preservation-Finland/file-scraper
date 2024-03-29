File Scraper Technical Notes
============================

Here are some notes about the technical functionality of the file-scraper tool.

Detectors
---------

The detectors are used for detecting the file mimetype and, if possible, format version. These values are used for selecting the correct scraper tools
for collecting metadata and checking well-formedness of the file. For now, there are just three detectors, all of which are located in ``./file_scraper/detectors.py``

The detectors inherit ``BaseDetector`` class, which contains an abstract method ``detect()``. A detector class:

    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * SHOULD detect mimetype of selected file formats and store it in mimetype attribute when ``detect()`` is called.
    * MAY detect also format version and store it in version attribute.

The ``info`` attribute contains a dict of class name and scraper software as well as messages and errors occured during detection.
See ``<scraper info X>`` from `README.rst <../README.rst>`_ for the content of the info attribute.

.. image:: scraper_tree.png

Graders
-------

Graders are used to assign a digital preservation grade for a file that has been scraped, and define if the file is suitable for digital preservation.
Graders are defined in ``./file_scraper/graders.py``.

The graders inherit ``BaseGrader``, which exposes the following methods:

    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * MUST implement ``is_supported(mimetype)`` to determine whether to grade the given file based on its MIME type.
    * MUST implement ``grade()`` to perform the actual grading and return the grade. The returned grade must be one of the grade constants defined in ``file_scraper.DEFAULTS``.

Each grader instance contains the ``mimetype``, ``version``, ``streams`` and ``scraper`` attributes that can be used to inspect the file and perform the grading.

Scraper tools
-------------

All the iterable and usable scraper tools are located in subdirectories of ``./file_scraper/`` directory. These scraper tools are based on ``BaseScraper``,
either by directly inheriting it, or via inheriting a tool specific base class that inherits ``BaseScraper``.

In the Figure above, ``GhostScriptScraper`` inherits ``BaseScraper`` directly, but ``JHoveGifScraper`` and ``JHoveHtmlScraper`` inherit it indirectly via ``JHoveScraperBase`` base class, as do other subclasses of JHoveScraperBase not shown in the Figure.
These scraper tools are located in ``./file_scraper/ghostscript/`` and ``./file_scraper/jhove/`` directories. When the used 3rd party tool is
file format specific, it can inherit ``BaseScraper`` directly, but in some cases writing an intermediate subclass is a justified decision. For example as different JHOVE modules are able to handle a number of file types, including the mentioned GIF and HTML files among others, we need custom handling for different file types. This is why each module has its own scraper that inherits the ``JHoveBaseScraper`` providing the core scraping function. In many cases a single scraper class supporting multiple metadata models for different file types can be sufficient though.

A usable scraper tool class:

    * MUST have ``_supported_metadata`` class variable which is a list of metadata classes supported by the scraper.
    * MUST have ``_only_wellformed = True`` class variable, if the scraper tools does just well-formed check.
    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * MUST implement ``scrape_file()`` for file scraping, if not implemented in the already existing base class. This method:

        * MUST add metadata objects of all metadata models to ``streams`` list for each stream in the file. The MIME type and version given in params MUST be passed to the metadata object.
        * SHOULD call ``_check_supported()`` when the metadata has been collected. This checks that the final mimetype and version are supported ones, in case those have changed.
        * MUST log all errors (e.g. ""The file is truncated" or ""File not found.") to ``_errors`` list and messages (e.g. "File was analyzed successfully") to ``_messages`` list.
    * The ``info()`` method of a scraper MUST return a dict of class name and used 3rd party software, and messages and errors occured during scraping. See ``<scraper info X>`` from `README.rst <../README.rst>`_ for the content of the info attribute.

The metadata is represented by metadata model objects, e.g. ``GhostscriptMeta`` used by ``GhostscriptScraper``, and ``JHoveGifMeta``, ``JHoveHtmlMeta`` and others used by ``JHoveScraper``. These metadata model classes:

    * MUST have _supported class variable as a dict, the keys of which are supported mimetypes and values are lists of supported file format versions.
    * Using the metadata model without prior knowledge of the version or with an unlisted version MAY be allowed by setting class variable ``_allow_versions = True``.
    * MUST have a method for each metadata element that is scraped, if not implemented in the already existing base class.
        * These methods MUST be decorated with ``metadata``-function, and MUST normally return string, with exception of ``index()`` which returns stream index as integer.
        * The metadata methods MUST normalize the value to a normalized format. The formats described e.g. in AudioMD [1]_, VideoMD [1]_, and MIX [2]_ are used in normalization.
        * The key of the metadata element in ``streams`` will be the method name, and value is the return value of the method.
        * Metadata method MAY raise ``SkipElement`` from ``file_scraper.base``, if the methods needs to be omitted in collection phase. This may become handy with files containing different kinds of streams. Value ``(:unav)`` is returned when a scraper cannot determine the value of a metadata element and ``(:unap)`` when the metadata element is not applicable to the stream type.
        * Example of a metadata method::

            @metadata
            def width(self):
                return self._width

    * MUST implement metadata method ``stream_type()``, returning e.g. "text", "image", "audio", "video", "videocontainer", "binary", if not implemented in the already existing base class.
    * MUST crash or log an error in unexpected event, such as due to missing 3rd party tool.
    * Metadata keys that are needed to win in the combination phase are flagged by ``important`` as part of metadata-decorator.
    * If custom MIME type scraping is implemented, user-supplied MIME type given to the initializer MUST be returned by ``mimetype()`` function if given.
    * If custom version scraping is implemented, user-supplied version must be returned by ``version()`` if both MIME type and version were given to the initializer. If MIME type or version was not given, the same version MUST be returned as would have been if neither had been given.

Should you create a new scraper tool for some file format, it probably already has a proper base class, for example:

    * ``PilScraper`` and ``WandScraper`` for images: You need to create a file format specific scraping tool for  both to create full metadata collection.
    * ``MediainfoScraper`` and ``FFMpegScraper`` for audio and video files: You can not use both for video container metadata scraping, since these tools return the streams in different order.
    * ``MagicScraper`` for a variety of files, including text and markup (HTML, XML) files, some image formats, pdf and office files.
    * ``JHoveScraper`` for various file formats: You may add a file format for JHove well-formed check, if applicable.
    * ``BaseScraper`` is generic base class for scrapers not suitable to use any of the previous ones for full scraping and for new tool specific base classes.

In practice, just add proper values to class variables, and write the ``scrape_file()`` method and metadata model class(es). The tool specific base classes already have ``scrape_file()`` method implemented. To maintain clarity, the new scraper classes and metadata models should be created into their tool-specific subdirectories under ``./file_scraper/``.

.. [1] https://www.loc.gov/standards/amdvmd/
.. [2] http://www.loc.gov/standards/mix/

Scraper sequence
----------------

The main scraper iterates all detectors to determine mimetype and possibly file format version. The results of the detectors are given to scraper iterator,
which forwards the values to ``is_supported()`` class method of the scraper. The ``is_supported()`` method makes the decision, whether its scraper is supported or not.
Supported scrapers are iterated, and the result of each scraper is combined directly to the final result. The resulted attributes are listed in `README.rst <../README.rst>`_.

The main Scraper does everything in sequenced order. Should the scraper functionality be done in parallel, this can be changed by modifying the Scraper class
and the utility functions it uses.

.. image:: scraper_seq.png

Scraping without checking well-formedness
-----------------------------------------

    * Individual scraper tools return always ``True`` or ``False`` as ``well_formed``, regardless of the use of ``check_wellformed`` parameter in main Scraper.
      The main Scraper resolves ``well_formed`` as ``None``, if the tool's result was ``True`` and ``check_wellformed`` parameter is ``False``.
      This is because all required scraper tools are not used when ``check_wellformed`` is ``False``.
      The ``is_supported()`` method in the tools solves whether a tool shoud be run or not, but otherwise the tools do not know which method is used in the main Scraper.
    * Scraping without checking well-formedness must still somehow detect the mimetype and version, and it must give error in ``info()``
      if the detection does not comply with the given file type. Mainly for this reason, some file format versions detected by the detectors
      (not ``PredefinedDetector``) are provided to a dummy scraper, which result this value for the main Scraper.

          * Example: If ``text/plain`` is given, but ``text/html`` is resolved, then well_formed must be ``True`` (in the end ``None``).
          * Example: If ``image/jpeg`` is given, but ``text/plain`` is resolved, then well_formed must be ``False`` (in the end ``False``).

A Few Guidelines for Resulting MIME Type (and version)
------------------------------------------------------

    * If the validator supports only one particular file format, then the scraper can result the mimetype as a string, if there are no errors.
      Then it means that the file is compliant with the only supported (and originally predefined) format.
      If there are errors, then the validator does not really know the mimetype, and therefore ``(:unav)`` should be returned.
    * If we give a PNG file predefined as GIF file, then a GIF scraper produces errors and PNG+GIF scraper does not.
      The GIF scraper can not give the mimetype, since it gives errors, and therefore it does not know what the file is.
      The PNG+GIF scraper can give the mimetype ONLY if it is able to resolve the mimetype.
    * If we give an XML file as a Plain text file, then Plain text scrapers are run.
      These should result either ``text/plain`` as mimetype, or ``(:unav)`` if they are not sure about it.
      For Plain text files this is actually possible only if the scraper is a plain text specific scraper and no errors are found.
    * If all the scrapers result ``(:unav)`` as mimetype, then the actual file format is unknown.
      There must be at least one scraper which resolves the mimetype and version.
    * If the predefined mimetype differs from the resulted one, then it is the main Scraper's responsibility to resolve this with an extra error message.
    * The same applies also to file format version.

Test Data
---------

When new test data is added under ``tests/data``, it is automatically discovered by ``tests/end_to_end_test.py``. These tests determine the expected scraping result based on the file name and path, so in order for these tests to pass, the files must follow the naming ::

    tests/data/<mime_type>/<well_formedness>_<version>_<description>.<extension>

where

* ``mime_type`` is the MIME type of the file with slash replaced with underscore, e.g. ``image_jpeg``
* ``well_formedness`` is either ``valid`` or ``invalid`` depending on whether the file is well-formed
* ``version`` is the version of the file type, e.g. `1.01`
* Everything that comes after the underscore following the version number is technically optional but should still be included for clarity, and ``description`` can be used e.g. to specify other relevant information about the file (e.g. why it is not well-formed, or relevant information about non-filetype metadata)
* ``extension`` is also not used by the tests, but it should be included for human-readability

