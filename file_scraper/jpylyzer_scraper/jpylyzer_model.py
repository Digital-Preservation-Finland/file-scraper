from file_scraper.base import BaseMeta

class JpylyzerMeta(BaseMeta):
    
    _supported = {"image/jp2": []}
    _allow_versions = True   # Allow any version

