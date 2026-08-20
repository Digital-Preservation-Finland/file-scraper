"""Extractor for various binary and text file formats."""

from os.path import getsize
from typing import TypeVar

from file_scraper.base import BaseExtractor
from file_scraper.magic_extractor.magic_model import (
    AiffFileMagicMeta,
    BaseMagicMeta,
    BinaryMagicBaseMeta,
    GifFileMagicMeta,
    HtmlFileMagicMeta,
    Jp2FileMagicMeta,
    JpegFileMagicMeta,
    OfficeFileMagicMeta,
    PdfFileMagicMeta,
    PngFileMagicMeta,
    TextFileMagicMeta,
    TextMagicBaseMeta,
    TiffFileMagicMeta,
    XhtmlFileMagicMeta,
    XmlFileMagicMeta,
)
from file_scraper.magiclib import magic_analyze, magiclib, magiclib_version

MagicMetaT = TypeVar("MagicMetaT", bound=BaseMagicMeta)


class MagicBaseExtractor(BaseExtractor[MagicMetaT]):
    """Extractor for scraping files using magic."""

    _allow_unav_mime = False
    _allow_unav_version = True
    _allow_unap_version = True

    @property
    def well_formed(self):
        """Magic is not able to check well-formedness.

        :returns: False if magic can not open or handle the file,
                  None otherwise.
        """
        valid = super().well_formed
        if not valid:
            return valid

        return None

    def _magic_call(self) -> dict:
        """Fetch three values from file with using magic.
        These are: mimetype, info line (for version) and encoding.

        :returns: Python dict of the three fetched values from magic
        """
        magic_lib = magiclib()
        magicdict = {
            "magic_mime_type": magic_lib.MAGIC_MIME_TYPE,
            "magic_none": magic_lib.MAGIC_NONE,
            "magic_mime_encoding": magic_lib.MAGIC_MIME_ENCODING
        }

        magic_result = {}
        for key, value in magicdict.items():
            magic_result[key] = magic_analyze(
                magic_lib,
                value,
                self.filename,
            )

        if (
            self.filename.suffix == ".json"
            and magic_result["magic_mime_type"] == "text/plain"
        ):
            # If a file ending in "".json" is detected as "text/plain", try to
            # detect mimetype again with MAGIC_PARAM_BYTES_MAX set to the file
            # size. JSON files larger than MAGIC_PARAM_BYTES_MAX (default 7 MB)
            # are detected as "text/plain".
            magic_result["magic_mime_type"] = magic_analyze(
                magic_lib,
                magic_lib.MAGIC_MIME_TYPE,
                self.filename,
                {magic_lib.MAGIC_PARAM_BYTES_MAX: getsize(self.filename)},
            )
        return magic_result

    def _extract(self) -> None:
        """Populate streams with supported metadata objects."""
        magic_result = self._magic_call()

        self.streams = list(self.iterate_models(
            magic_result=magic_result,
            predefined_mimetype=self._predefined_mimetype,
        ))

    def tools(self) -> dict[str, dict[str, str]]:
        """Return information about the software used by the extractor or
        detector.

        :returns: Dictionary where each key is the name of the software tool,
            and each value is another dictionary containing details about the
            tool (e.g. version). If no tools are available, an empty
            dictionary is returned instead.
        """
        return {"libmagic": {"version": magiclib_version()}}


class MagicTextExtractor(MagicBaseExtractor[TextMagicBaseMeta]):
    """
    Magic extractor for text files.

    We have to allow (:unav) mimetype for text files, since we are not quite
    sure about the final mimetype. An XML file may also be plain text file.
    """

    _allow_unav_mime = True
    _supported_metadata: list[type[TextMagicBaseMeta]] = [
        TextFileMagicMeta,
        XmlFileMagicMeta,
        XhtmlFileMagicMeta,
        HtmlFileMagicMeta,
    ]


class MagicBinaryExtractor(MagicBaseExtractor[BinaryMagicBaseMeta]):
    """
    Magic extractor for binary files.

    Currently, these are all mime types which can not be anything else at the
    same time. Therefore it is pretty safe to disallow (:unav) as a mimetype
    result.
    """

    _supported_metadata: list[type[BinaryMagicBaseMeta]] = [
        PdfFileMagicMeta,
        OfficeFileMagicMeta,
        PngFileMagicMeta,
        JpegFileMagicMeta,
        Jp2FileMagicMeta,
        TiffFileMagicMeta,
        GifFileMagicMeta,
        AiffFileMagicMeta,
    ]
