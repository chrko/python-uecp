import enum
import typing

from uecp.commands.base import (
    UECPCommand,
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)
from uecp.commands.mixins import InvalidDataSetNumber


class SiteEncoderAddressSetCommandMode(enum.IntEnum):
    REMOVE_SINGLE = 0b00
    ADD_SINGLE = 0b01
    REMOVE_ALL = 0b10


@UECPCommand.register_type
class SiteAddressSetCommand(UECPCommand):
    ELEMENT_CODE = 0x23

    def __init__(self, mode: SiteEncoderAddressSetCommandMode, site_address: int):
        self._mode: SiteEncoderAddressSetCommandMode = (
            SiteEncoderAddressSetCommandMode.ADD_SINGLE
        )
        self._site_address = 0
        self.mode = mode
        self.site_address = site_address

    @property
    def mode(self) -> SiteEncoderAddressSetCommandMode:
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = SiteEncoderAddressSetCommandMode(value)

    @property
    def site_address(self) -> int:
        return self._site_address

    @site_address.setter
    def site_address(self, value):
        value = int(value)
        if not (0 <= value <= 0x3FF):
            raise ValueError(
                f"Site address must be in range of 0 to 0x3ff, {value:#x} given"
            )
        self._site_address = value

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            int(self._mode),
            self._site_address >> 8,
            self._site_address & 0xFF,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("SiteAddressSetCommand", int):
        data = list(data)
        if len(data) < 4:
            raise UECPCommandDecodeNotEnoughData(len(data), 4)
        mec, mode, site_address_high, site_address_low = data[0:4]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        site_address = site_address_high << 8 | site_address_low
        return cls(mode=mode, site_address=site_address), 4


@UECPCommand.register_type
class EncoderAddressSetCommand(UECPCommand):
    ELEMENT_CODE = 0x27

    def __init__(self, mode: SiteEncoderAddressSetCommandMode, encoder_address: int):
        self._mode: SiteEncoderAddressSetCommandMode = (
            SiteEncoderAddressSetCommandMode.ADD_SINGLE
        )
        self._encoder_address = 0
        self.mode = mode
        self.encoder_address = encoder_address

    @property
    def mode(self) -> SiteEncoderAddressSetCommandMode:
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = SiteEncoderAddressSetCommandMode(value)

    @property
    def encoder_address(self) -> int:
        return self._encoder_address

    @encoder_address.setter
    def encoder_address(self, value):
        value = int(value)
        if not (0 <= value <= 0x3F):
            raise ValueError(
                f"Encoder address must be in range of 0 to 0x3f, {value:#x} given"
            )
        self._encoder_address = value

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            int(self._mode),
            self._encoder_address,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("EncoderAddressSetCommand", int):
        data = list(data)
        if len(data) < 3:
            raise UECPCommandDecodeNotEnoughData(len(data), 3)
        mec, mode, encoder_address = data[0:3]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        return cls(mode=mode, encoder_address=encoder_address), 3


@enum.unique
class CommunicationMode(enum.IntEnum):
    UNIDIRECTIONAL = 0
    BIDIRECTIONAL_REQUESTED_RESPONSE = 1
    BIDIRECTIONAL_SPONTANEOUS_RESPONSE = 2


@UECPCommand.register_type
class CommunicationModeSetCommand(UECPCommand):
    ELEMENT_CODE = 0x2C

    def __init__(self, mode: CommunicationMode):
        self._mode = CommunicationMode(mode)

    @property
    def mode(self) -> CommunicationMode:
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = CommunicationMode(value)

    def encode(self) -> list[int]:
        return [self.ELEMENT_CODE, int(self._mode)]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("CommunicationModeSetCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, mode = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        return cls(mode=mode), 2


@UECPCommand.register_type
class DataSetSelectCommand(UECPCommand):
    ELEMENT_CODE = 0x1C

    def __init__(self, data_set_number: int):
        self._data_set_number = 0
        self.data_set_number = data_set_number

    @property
    def data_set_number(self) -> int:
        return self._data_set_number

    @data_set_number.setter
    def data_set_number(self, new_data_set_number: int):
        try:
            if new_data_set_number == int(new_data_set_number):
                new_data_set_number = int(new_data_set_number)
            else:
                raise ValueError()
        except ValueError:
            raise InvalidDataSetNumber(new_data_set_number)

        if not (0x00 <= new_data_set_number <= 0xFF):
            raise InvalidDataSetNumber(new_data_set_number)
        self._data_set_number = new_data_set_number

    def encode(self) -> list[int]:
        return [self.ELEMENT_CODE, self._data_set_number]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("DataSetSelectCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, data_set_number = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        return cls(data_set_number=data_set_number), 2
