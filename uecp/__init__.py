"""UECP encoder & decoder"""

__version__ = "0.0.1"

import abc


class UECPMessage(abc.ABC):
    ELEMENT_CODE = ...
    ELEMENT_CODE_MAP: dict[int, "UECPMessage"] = {}

    @abc.abstractmethod
    def encode(self) -> list[int]:
        ...

    @classmethod
    @abc.abstractmethod
    def create_from(cls, data: bytes) -> ("UECPMessage", int):
        ...
