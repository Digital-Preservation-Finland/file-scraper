"""file-scraper module."""
try:
    from ._version import version as __version__
except ImportError:
    # Package not installed
    __version__ = "unknown"
