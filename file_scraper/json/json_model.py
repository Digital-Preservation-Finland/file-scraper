from file_scraper.base import BaseMeta
from file_scraper.utils import metadata
from dpres_file_formats.defaults import UnknownValue as Unkn


class JsonMeta(BaseMeta):
    """
    All metadata is formalized in common data model.

    BaseMeta class will define common metadata for all file formats, such as:
    filename, mimetype, version, checksum.

    Additional metadata and processing is implemented in subclasses.
    """

    _supported: dict[str, list[str]] = {"application/json": [Unkn.UNAP]}
    _allow_versions = False

    @metadata()
    def stream_type(self):
        """
        Return file type.
        """
        return "text"

    @metadata()
    def mimetype(self) -> str:
        return "application/json"

    @metadata()
    def version(self) -> str:
        """
        Json format doesn't have a version so the version doesn't make sense

        :returns: "(:unap)"
        """
        return Unkn.UNAP
