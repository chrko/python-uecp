"""UECP encoder & decoder"""

__version__ = "0.4.0"

# import custom codecs to ensure registering search functions
from uecp import byte_stuffing_codec, rds_character_set_codec  # noqa: F401

__all__: list[str] = []
