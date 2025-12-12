from file_scraper.base import BaseExtractor
from file_scraper.json.json_model import JsonMeta
import json


class JsonExtractor(BaseExtractor):
    """Json extractor. Extracts if the given file is a json file"""

    _supported_metadata: list[type[JsonMeta]] = [JsonMeta]
    _only_wellformed = False

    def extract(self):
        with open(self.filename, "rt") as file:
            try:
                json.loads(file.read())
                self._messages.append("The file is a valid JSON document")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self._errors.append(
                    f"{self.__class__.__name__} produced an error: {e}"
                )

        self.streams = list(self.iterate_models())
        self._validate(allow_unap_version=True)

    def tools(self) -> dict:
        return {}
