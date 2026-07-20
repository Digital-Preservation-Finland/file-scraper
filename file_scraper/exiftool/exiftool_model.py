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

    @BaseMeta.metadata()
    def stream_type(self):
        """Return file type."""
        return "image"


class ExifToolExifMeta(ExifToolBaseMeta):
    """
    Metadata models for Exif image files (i.e. JPEG/Exif)
    """

    _supported = {
        "image/jpeg": ["2.0", "2.1", "2.2", "2.2.1", "2.3", "2.3.1", "2.3.2"]
    }

    # JPEG file can have both JFIF and Exif app segments.
    # If both exist, Exif takes precedence.
    @BaseMeta.metadata()
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

    @BaseMeta.metadata()
    def mimetype(self):
        """
        Return mimetype.

        Decorator is marked as important because other extractors may not
        recognize the mimetype of a dng file as dng, but tiff. This way a
        conflict can be avoided and the mimetype of dng files will be scraped
        correctly when merging the results from different extractors.
        """
        return super().mimetype()

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

    @BaseMeta.metadata()
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


class ExifToolGeoTiffMeta(ExifToolBaseMeta):
    """Metadata model for GeoTIFF files"""

    _supported = {"image/tiff": ["1.1"]}
    _allow_any_version = False

    @BaseMeta.metadata()
    def samples_per_pixel(self) -> str:
        """Return TIFF SamplesPerPixel."""
        value = self._metadata.get("EXIF:SamplesPerPixel")
        return str(value) if value is not None else UNAV

    @BaseMeta.metadata()
    def bps_unit(self):
        """Return BitsPerSample unit."""
        sample_format = self._metadata.get("EXIF:SampleFormat")

        if not sample_format:
            return UNAV

        if isinstance(sample_format, str):
            sample_format = int(sample_format.split()[0])

        # For TIFF images, possible values are:
        # 1 - Unsigned integer
        # 2 - Signed integer
        # 3 - IEE floating point
        # 4 - Undefined

        if sample_format == 3:
            return "floating point"

        if sample_format in {1, 2}:
            return "integer"

        return UNAV

    @BaseMeta.metadata()
    def bps_value(self) -> str:
        """Return BitsPerSample."""
        value = self._metadata.get("EXIF:BitsPerSample")
        if not value:
            return UNAV

        if isinstance(value, str):
            return value.split()[0]

        return str(value)

    @BaseMeta.metadata()
    def byte_order(self) -> str:
        """Return TIFF byte order."""
        value = self._metadata.get("File:ExifByteOrder")

        mapping = {
            "II": "little endian",
            "MM": "big endian",
        }

        return mapping.get(value, UNAV)

    @BaseMeta.metadata()
    def compression(self) -> str:
        """Return compression type."""
        value = self._metadata.get("EXIF:Compression")

        mapping = {
            1: "no",
            5: "lzw",
            7: "jpeg",
            8: "zip",
        }

        return mapping.get(value, str(value) if value else UNAV)

    @BaseMeta.metadata()
    def colorspace(self) -> str:
        """Return colorspace."""
        value = self._metadata.get("EXIF:PhotometricInterpretation")

        mapping = {
            0: "whiteiszero",
            1: "gray",
            2: "rgb",
            3: "palette",
            5: "cmyk",
            6: "ycbcr",
        }

        return mapping.get(value, UNAV)

    @BaseMeta.metadata()
    def version(self) -> str:
        """Return version."""
        if self._metadata.get("GeoTiff:GeoTiffVersion") is not None:
            return "1.1"
        return UNAV
