""""Extractor for jp2 files using Jpylyzer."""
try:
    from jpylyzer import jpylyzer
except ImportError:
    pass
import xml.etree.ElementTree as ET

from file_scraper.base import BaseExtractor
from file_scraper.jpylyzer.jpylyzer_model import JpylyzerMeta
from file_scraper.utils import ensure_text


class JpylyzerExtractor(BaseExtractor):
    """Extractor to check the wellformedness of jp2 files."""
    _supported_metadata = [JpylyzerMeta]
    _only_wellformed = True   # Only well-formed check

    def extract(self):
        """Scrape data from file."""
        try:
            result = jpylyzer.checkOneFile(self.filename)
            well_formed = result.findtext("./isValid")
            if well_formed == "True":
                self._messages.append("File is well-formed and valid.")
            else:
                self._errors.append("Failed: document is not well-formed.")
                self._errors.append(ensure_text(ET.tostring(result)))
        except Exception as exception:  # pylint: disable=broad-except
            self._errors.append("Failed: error analyzing file.")
            self._errors.append(str(exception))

        self.streams = list(self.iterate_models())
        self._check_supported(allow_unav_mime=True,
                              allow_unav_version=True,
                              allow_unap_version=True)

    def tools(self):
        """
        Overwriting baseclass implementation
        to collect information about software used by the extractor

        :returns: a dictionary with the used software or UNAV.
        """
        return {"jpylyzer":
                {
                        "version": jpylyzer.__version__
                    }
                }
