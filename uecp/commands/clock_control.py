import struct
import typing
import zoneinfo
from datetime import datetime, timedelta, timezone

from uecp.commands import UECPCommand
from uecp.commands.base import (
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)


@UECPCommand.register_type
class RealTimeClockSetCommand(UECPCommand):
    ELEMENT_CODE = 0x0D

    UTC = zoneinfo.ZoneInfo("UTC")

    def __init__(self, timestamp: typing.Optional[datetime] = None):
        self._timestamp = datetime.now(self.UTC)
        self.timestamp = timestamp

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: typing.Optional[datetime]):
        if value is None:
            self._timestamp = datetime.now(self.UTC)
            return
        if value.tzinfo is None:
            raise ValueError("Missing timezone")
        self._timestamp = value

    def encode(self) -> list[int]:
        ts = self._timestamp.astimezone(self.UTC)
        data = [
            self.ELEMENT_CODE,
            ts.year % 100,
            ts.month,
            ts.day,
            ts.hour,
            ts.minute,
            ts.second,
            round(ts.microsecond / 10_000),
            self._encode_localtime_offset(self._timestamp.utcoffset()),
        ]

        return data

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RealTimeClockSetCommand", int):
        data = list(data)
        if len(data) < 9:
            raise UECPCommandDecodeNotEnoughData(len(data), 9)

        (
            mec,
            year,
            month,
            day,
            hour,
            minute,
            second,
            centisecond,
            encoded_localtime_offset,
        ) = data

        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        offset = cls._decode_localtime_offset(encoded_localtime_offset)
        timestamp = datetime(
            year=year + 2000,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=centisecond * 10_000,
            tzinfo=cls.UTC,
        ).astimezone(timezone(offset))

        return cls(timestamp=timestamp), 9

    @staticmethod
    def _encode_localtime_offset(offset: timedelta):
        offset_seconds = offset.total_seconds()
        sign = offset_seconds < 0

        localtime_offset = (sign << 6) | abs(round(offset_seconds / 1800))

        return localtime_offset

    @staticmethod
    def _decode_localtime_offset(encoded_localtime_offset: int) -> timedelta:
        if not (0x00 <= encoded_localtime_offset <= 0x3F):
            raise ValueError(f"{encoded_localtime_offset:x} not in [0x00, 0x3f]")

        sign = -1 if encoded_localtime_offset & (1 << 6) else 1
        offset_seconds = sign * (encoded_localtime_offset & 0b11111) * 1800

        return timedelta(seconds=offset_seconds)


@UECPCommand.register_type
class RealTimeClockCorrectionSetCommand(UECPCommand):
    ELEMENT_CODE = 0x09

    _STRUCT = struct.Struct(">h")

    def __init__(self, adjustment_ms: 0):
        self._adjustment_ms = 0
        self.adjustment_ms = adjustment_ms

    @property
    def adjustment_ms(self) -> int:
        return self._adjustment_ms

    @adjustment_ms.setter
    def adjustment_ms(self, value):
        if not (-32768 <= value <= 32767):
            raise ValueError()
        self._adjustment_ms = int(value)

    def encode(self) -> list[int]:
        return [self.ELEMENT_CODE] + list(self._STRUCT.pack(self._adjustment_ms))

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RealTimeClockCorrectionSetCommand", int):
        data = list(data)
        if len(data) < 3:
            raise UECPCommandDecodeNotEnoughData(len(data), 3)
        mec = data[0]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        adjustment_ms = cls._STRUCT.unpack(bytes(data[1:3]))[0]

        return cls(adjustment_ms=adjustment_ms), 3


@UECPCommand.register_type
class RealTimeClockEnabledSetCommand(UECPCommand):
    ELEMENT_CODE = 0x19

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
    ) -> ("RealTimeClockEnabledSetCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, enable = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        if enable not in (0x00, 0x01):
            raise ValueError("Not allowed value decoded")
        return cls(enable=enable), 2
