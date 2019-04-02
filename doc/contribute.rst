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

.. image:: scraper_tree.png

Scraper tools
-------------

All the iterable and usable scraper tools are located in ``./file_scraper/scrapers/`` directory. These scraper tools are based on ``BaseScraper``,
either with directly inheriting it, or via tool specific base class.

In the Figure above, ``GhostScript`` scraper tool inherits ``BaseScraper`` directly, but ``TiffWand`` and ``ImageWand`` inherit it indirectly via ``Wand`` base class.
Here, ``GhostScript``, ``TiffWand`` and ``ImageWand`` are the scraper tools located in ``./file_scraper/scrapers/`` directory. When the used 3rd party tool is
file format specific, it can inherit ``BaseScraper`` directly, but with ``Wand``, we need to handle TIFF images in a diffrent way from the other image formats.
This is why the actual functionality is done in the separate tool specific base class ``Wand``, and then the file format specific tools are able to inherit it.

Should you create a new scraper tool for some file format, it probably already has a proper base class, for example:

    * ``Pil`` and ``Wand`` for images: You need to create a file format specific scraping tool for  both to create full metadata collection.
    * ``Mediainfo`` and ``FFMpeg`` for audio and video files: You can not use both for video container metadata scraping, since these tools return the streams in different order.
    * ``TextMagic`` for text files: Finds out the charset of the file and checks mimetype and version.
    * ``BinaryMagic`` for binary files: Checks mimetype and version, if not checked well enough in the actual well-formed check.
    * ``JHove`` for various file formats: You may add a file format for JHove well-formed check, if applicable.
    * ``BaseScraper`` is generic base class for scrapers not suitable to use any of the previous ones for full scraping and for new tool specific base classes.

In practice, just add proper values to class variables and override the needed metadata methods. The tool specific base classes already have ``scrape_file()`` method implemented.

To maintain clarity, do not allow a tool specific base class to support any mimetype, and keep it away from ``./file_scraper/scrapers/`` directory. Instead,
add the base class to ``./file_scraper/`` and create separate mimetype specific classes to inherit it.

A usable scraper tool class:

    * MUST have ``_supported`` class variable as a dict, which keys are supported mimetypes and values are lists of supported file format versions.
    * MUST have ``_only_wellformed = True`` class variable, if the scraper tools does just well-formed check.
    * The scraper is normally launched also with other version numbers than listed (e.g. with ``None``).
      This MAY be disallowed with a class variable ``_allow_versions = False``.
    * MUST call ``super()`` during initialization, if separate initialization method is created.
    * MUST implement ``scrape_file()`` for file scraping, if not implemented in the already existing base class:

        * SHOULD call ``_check_supported()`` as the second last command of ``scrape_file()``. This checks that the final mimetype and version are supported ones, in case those
          have changed. This MAY be omitted, if ``check_wellformed`` is ``False``.
        * MUST call ``_collect_elements()`` as the last command of ``scrape_file()`` regardless of the validation result.
          This will collect the metadata to ``streams`` attribute.

    * MUST have a method for each metadata element that is needed to be resulted, if not implemented in the already existing base class.
      These methods MUST be named with ``_`` prefix and decorated with ``metadata``-function, e.g. ``_width()``, and MUST normally return string, with exception of ``_index()`` which returns stream index as integer.
      The metadata methods must normalize the value to a normalized format. The formats described e.g. in AudioMD [1]_, VideoMD [1]_, and MIX [2]_ are used in normalization.
      The ``_collect_elements()`` in ``BaseScraper`` will collect the return values from all ``metadata``-decorated methods with ``_`` prefix automatically to ``streams`` attribute.
      The key of the metadata element in ``streams`` will be the method name without ``_`` prefix (e.g. ``width``), and value is the return value of the method.
      Metadata method MAY raise ``SkipElement`` from ``file_scraper.base``, if the methods needs to be omitted in
      collection phase. This may become handy with files containing different kinds of streams. The value ``None`` is used for the case that the value SHOULD be returned,
      but the scraper tool is not capable to do that. Example:

.. code-block::

    @metadata
    def _width():
        return self._width
..

    * MUST implement metadata ``_stream_type()``, returning e.g. "text", "image", "audio", "video", "videocontainer", "binary", if not implemented in the already existing base class.
    * MUST use ``errors()`` for error messages and ``messages()`` for info messages.
    * MUST crash in unexpected event, such as due to missing 3rd party tool.
    * Methods ``iter_tool_streams()`` and ``set_tool_streams()`` MUST be implemented to iterate and select stream from the 3rd party tool,
      if the 3rd party tool is able to result several streams, and if this is not implemented in existing base class.
      These must cause the ``_`` prefixed metadata methods to return value from the current stream.
    * Metadata keys that are needed to win in the combination phase is flagged by ``important`` as part of metadata-decorator.
      By default, scraper will update the important list as it goes through the metadata. The list can then be fetched via ``importants()``-method.
      Scrapers can override the default behaviour of ``importants()`` in their own class.

The ``info`` attribute contains a dict of class name, and messages and errors occured during scraping.
See ``<scraper info X>`` from `README.rst <../README.rst>`_ for the content of the info attribute.

.. [1] https://www.loc.gov/standards/amdvmd/
.. [2] http://www.loc.gov/standards/mix/

Scraper sequence
----------------

The main scraper iterates all detectors to determine mimetype and possibly file format version. The results of the detectors are given to scraper iterator,
which forwards the values to ``is_supported()`` class method of the scraper. The ``is_supported()`` method makes the decision, whether it's scraper is supported or not.
Supported scrapers are iterated, and the result of each scraper is combined directly to the final result. The resulted attributes are listed in `README.rst <../README.rst>`_.

The main Scraper does everything in sequenced order. Should the scraper functionality be done in parallel, this can be changed by modifying the Scraper class
and the utility functions it uses.

.. image:: scraper_seq.png
