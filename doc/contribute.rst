File Scraper Technical Notes
============================

Here are some notes about the technical functionality of the file-scraper tool.

Detectors
---------

The detectors are used for detecting the file mimetype and, if possible, format version. These values are used for selecting the correct scraper tools
for collecting metadata and checking well-formedness of the file. For now, there exists just two detectors, and both are located in ``./file_scraper/detectors.py``

The detectors inherit ``BaseDetector`` class, which contains an abstract method ``detect()``. A detector class:

    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * MUST detect mimetype of selected file formats and store it in mimetype attribute when ``detect()`` is called.
    * MAY detect also format version and store it in version attribute.

The ``info`` attribute contains a dict of class name, and messages and errors occured during detection.
See ``<scraper info X>`` from `README.rst <../README.rst>`_ for the content of the info attribute.

Scraper tools
-------------

All the iterable and usable scraper tools are located in ``./file_scraper/scrapers/`` directory. These scraper tools are based on ``BaseScraper``,
either with directly inheriting it, or via tool specific base class.

.. image:: scraper_tree.png

In the Figure, ``GhostScript`` scraper tool inherits ``BaseScraper`` directly, but ``TiffWand`` and ``ImageWand`` inherit it indirectly via ``Wand`` base class.
Here, ``GhostScript``, ``TiffWand`` and ``ImageWand`` are the scraper tools located in ``./file_scraper/scrapers/`` directory. When the used 3rd party tool is
file format specific, it can inherit ``BaseScraper`` directly, but with ``Wand``, we need to handle TIFF images in a diffrent way from the other image formats.
This is why the actual functionality is done in the separate tool specific base class ``Wand``, and then the file format specific tools are able to inherit it.
To maintain clarity, do not allow a tool specific base class to support any mimetype, and keep it away from ``./file_scraper/scrapers/`` directory. Instead,
add the base class to ``./file_scraper/`` and create separate mimetype specific classes to inherit it.

A usable scraper tool class:

    * MUST have ``_supported`` class variable as a dict, which keys are supported mimetypes and values are lists of supported file format versions.
    * MUST have ``_only_wellformed = True`` class variable, if the scraper tools does just well-formed check.
    * The scraper is normally launched also with other version numbers than listed (e.g. with ``None``).
      This MAY be disallowed with a class variable ``_allow_versions = False``.
    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * MUST implement ``scrape_file()`` for file scraping.
    * SHOULD call ``_check_supported()`` as the second last command of ``scrape_file()``. This checks that the final mimetype and version are supported ones, in case those
      have changed. This MAY be omitted, if ``check_wellformed`` is ``False``.
    * MUST have a method for each metadata element that is needed to be resulted. These methods MUST be named with ``_s_`` prefix, e.g. ``_s_width()``, and MUST return string.
      The ``_collect_elements()`` in BaseScraper will collect the return values from all methods with ``_s_`` prefix automatically to ``streams`` attribute.
      The key of the metadata element in ``streams`` will be the method name without ``_s_`` prefix (e.g. ``width``), and value is the return value of the method.
      A ``_s_`` prefixed method MAY return ``SkipElement`` class (just class, not instance of a class) from file_scraper.base, if the methods needs to be omitted in
      collection phase. This may become handy with files containing different kinds of streams.
    * MUST implemet ``_s_stream_type()``, returning e.g. "text", "image", "audio", "video", "videocontainer", "binary".
    * MUST call ``_collect_elements()`` as the last command of ``scrape_file()`` regardless of the validation result.
      This will collect the metadata to ``streams`` attribute.
    * Methods ``iter_tool_streams()`` and ``set_tool_streams()`` MUST be implemented to iterate and select stream from the 3rd party tool,
      if the 3rd party tool is able to result several streams. These must cause the ``_s_`` prefixed methods to return value from the current stream.
    * Method ``get_important()`` MUST return a dict of those elements, which are needed to win in the combination phase.
      The keys of the dict must correspond to the keys of streams dict.

The ``info`` attribute contains a dict of class name, and messages and errors occured during scraping.
See ``<scraper info X>`` from `README.rst <../README.rst>`_ for the content of the info attribute.

Scraper sequence
----------------

The main scraper iterates all detectors to determine mimetype and possibly file format version. The results of the detectors are given to scraper iterator,
which forwards the values to ``is_supported()`` class method of the scraper. The ``is_supported()`` method makes the decision, whether it's scraper is supported or not.
Supported scrapers are iterated, and the result of each scraper is combined directly to the final result. The resulted attributes are listed in `README.rst <../README.rst>`_.

The main Scraper does everything in sequenced order. Should the scraper functionality be done in parallel, this can be changed by modifying the Scraper class
and the utility functions it uses.

.. image:: scraper_seq.png
