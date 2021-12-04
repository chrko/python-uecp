import typing

from uecp.commands.base import (
    UECPCommand,
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)


@UECPCommand.register_type
class RDSEnabledSetCommand(UECPCommand):
    ELEMENT_CODE = 0x1E

    def __init__(self, enable: bool):
        self._enable = bool(enable)

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = bool(value)

    def encode(self) -> list[int]:
        return [self.ELEMENT_CODE, int(self._enable)]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RDSEnabledSetCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, enable = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        if enable not in (0x00, 0x01):
            raise ValueError("Not allowed value decoded")
        return cls(enable=enable), 2


@UECPCommand.register_type
class RDSPhaseSetCommand(UECPCommand):
    ELEMENT_CODE = 0x22

    ALL_REFERENCE_TABLES = 0
    CURRENT_REFERENCE_TABLE = 7

    def __init__(self, reference_table: int, deci_degrees: int):
        self._reference_table = 0
        self.reference_table = reference_table
        self._deci_degrees = 0
        self.deci_degrees = deci_degrees

    @property
    def reference_table(self):
        return self._reference_table

    @reference_table.setter
    def reference_table(self, value):
        if not (0 <= value <= 7):
            raise ValueError()
        self._reference_table = value

    @property
    def deci_degrees(self):
        return self._deci_degrees

    @deci_degrees.setter
    def deci_degrees(self, value):
        if not (0 <= value <= 3599):
            raise ValueError()
        self._deci_degrees = int(value)

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            ((self._reference_table << 5) | (self._deci_degrees >> 8)),
            self._deci_degrees & 0xFF,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RDSPhaseSetCommand", int):
        data = list(data)
        if len(data) < 3:
            raise UECPCommandDecodeNotEnoughData(len(data), 3)
        mec = data[0]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        reference_table = (data[1] & (0b111 << 5)) >> 5
        deci_degrees = (data[1] & 0b1111) << 8 | data[2]

        return cls(reference_table=reference_table, deci_degrees=deci_degrees), 3


@UECPCommand.register_type
class RDSLevelSetCommand(UECPCommand):
    ELEMENT_CODE = 0x0E

    def __init__(self, reference_table: int, level: int):
        self._reference_table = 0
        self.reference_table = reference_table
        self._level = 0
        self.level = level

    @property
    def reference_table(self):
        return self._reference_table

    @reference_table.setter
    def reference_table(self, value):
        if not (0 <= value <= 7):
            raise ValueError()
        self._reference_table = value

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if not (0 <= value <= 8191):
            raise ValueError()
        self._level = int(value)

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            (self.reference_table << 5) | (self._level >> 8),
            self._level & 0xFF,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RDSLevelSetCommand", int):
        data = list(data)
        if len(data) < 3:
            raise UECPCommandDecodeNotEnoughData(len(data), 3)
        mec = data[0]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        reference_table = (data[1] & 0b1110_0000) >> 5
        level = (data[1] & 0b11111) << 8 | data[2]

        return cls(reference_table=reference_table, level=level), 3
