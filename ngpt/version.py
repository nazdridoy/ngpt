from importlib.metadata import version as get_version

try:
    __version__ = get_version("ngpt")
except ImportError:
    __version__ = "unknown" 