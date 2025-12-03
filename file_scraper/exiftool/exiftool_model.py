"""Metadata models for ExifTool"""


from file_scraper.base import BaseMeta
from file_scraper.defaults import UNAV
from file_scraper.utils import parse_exif_version


class ExifToolBaseMeta(BaseMeta):
    """
    Metadata models for files scraped with ExifTool.
    """
    def __init__(self, metadata):
        self._metadata = metadata

    @BaseMeta.metadata()
    def mimetype(self):
        return self._metadata.get("File:MIMEType", UNAV)


class ExifToolExifMeta(ExifToolBaseMeta):
    """
    Metadata models for Exif image files (i.e. JPEG/Exif)
    """

    _supported = {
        "image/jpeg": ["2.0", "2.1", "2.2", "2.2.1", "2.3", "2.3.1", "2.3.2"]
    }

    # JPEG file can have both JFIF and Exif app segments.
    # If both exist, Exif takes precedence.
    @BaseMeta.metadata(important=True)
    def version(self):
        """
        Return version.

        Version is converted to X.Y.Z format
        (eg. "0230" -> "2.3.0" and "0231" -> "2.3.1").
        This differs from Exif spec which combines major and minor parts from
        both (eg. "0230" -> "2.3" and "0231" -> "2.31").
        """
        if "EXIF:ExifVersion" in self._metadata:
            raw_version = self._metadata["EXIF:ExifVersion"]

            return parse_exif_version(raw_version)

        return UNAV


class ExifToolDngMeta(ExifToolBaseMeta):
    """
    Metadata models for dng files scraped with ExifTool.
    """

    _supported = {"image/x-adobe-dng": ["1.1", "1.2", "1.3", "1.4", "1.5"]}
    _allow_any_version = True

    @BaseMeta.metadata(important=True)
    def mimetype(self):
        """
        Return mimetype.

        Decorator is marked as important because other extractors may not
        recognize the mimetype of a dng file as dng, but tiff. This way a
        conflict can be avoided and the mimetype of dng files will be scraped
        correctly when merging the results from different extractors.
        """
        return super().mimetype()

    @BaseMeta.metadata(important=True)
    def version(self):
        """
        Return version with one decimal digit, eg. "1.3".

        Decorator is marked as important because other extractors may not
        recognize the version of a dng file correctly.
        """
        if "EXIF:DNGVersion" in self._metadata:
            version = self._metadata["EXIF:DNGVersion"].replace(" ", ".")
            return version[:3]
        return UNAV

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "image"

    @BaseMeta.metadata()
    def byte_order(self):
        """
        Return the byte order of the image.

        :returns: "big endian or "little endian" for images, (:unav) if there
                   is no image or if the byte order is unknown/unsupported.
        """
        value = self._metadata.get("File:ExifByteOrder", UNAV)
        if value == "II":
            return "little endian"
        if value == "MM":
            return "big endian"
        return UNAV
