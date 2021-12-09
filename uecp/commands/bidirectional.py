import enum
import typing

from uecp.commands import UECPCommand
from uecp.commands.base import (
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)


@enum.unique
class ResponseCode(enum.IntEnum):
    OK = 0
    CRC_ERROR = 1
    MSG_NOT_RECEIVED = 2
    MSG_UNKNOWN = 3
    DSN_ERROR = 4
    PSN_ERROR = 5
    PARAM_OUT_OF_RANGE = 6
    MSG_ELEMENT_LENGTH_ERROR = 7
    MSG_FIELD_LENGTH_ERROR = 8
    MSG_NOT_ACCEPTABLE = 9
    END_MSG_MISSING = 10
    BUFFER_OVERFLOW = 11
    BAD_STUFFING = 12
    UNEXPECTED_END_OF_MSG = 13


class MessageAcknowledgementCommand(UECPCommand):
    ELEMENT_CODE = 0x18

    def __init__(self, code: ResponseCode, sequence_counter: int = 0):
        self._code = ResponseCode(code)
        self._sequence_counter = 0
        self.sequence_counter = sequence_counter

    @property
    def code(self) -> ResponseCode:
        return self._code

    @code.setter
    def code(self, value):
        self._code = ResponseCode(value)

    @property
    def sequence_counter(self) -> int:
        return self._sequence_counter

    @sequence_counter.setter
    def sequence_counter(self, new_sequence_counter: int):
        if not (0 <= new_sequence_counter <= 0xFF):
            raise ValueError(
                f"Sequence counter must be in range of 0 to 0xff, {new_sequence_counter:#x} given"
            )
        if new_sequence_counter != int(new_sequence_counter):
            raise ValueError("Sequence counter must be an integer")
        self._sequence_counter = int(new_sequence_counter)

    def encode(self) -> list[int]:
        if self._code is not ResponseCode.OK:
            return [self.ELEMENT_CODE, int(self._code), self._sequence_counter]
        else:
            return [self.ELEMENT_CODE, 0]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("MessageAcknowledgementCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, code = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        code = ResponseCode(code)
        if code is ResponseCode.OK:
            return cls(code=code), 2
        if len(data) < 3:
            raise UECPCommandDecodeNotEnoughData(len(data), 3)
        sequence_counter = data[2]
        return cls(code=code, sequence_counter=sequence_counter), 3


@UECPCommand.register_type
class RequestCommand(UECPCommand):
    ELEMENT_CODE = 0x17

    def __init__(
        self,
        *,
        element_code: int = None,
        command: UECPCommand = None,
        data_set_number: int = None,
        programme_service_number: int = None,
        additional_data: typing.Union[bytes, list[int]] = None,
    ):
        if element_code is not None:
            if command is not None:
                raise ValueError(
                    "element_code and command are mutually exclusive required"
                )
            if element_code not in UECPCommand.ELEMENT_CODE_MAP:
                raise ValueError(f"Unknown element code {element_code:#x}")
            command = UECPCommand.ELEMENT_CODE_MAP[element_code]
        if command is None:
            raise ValueError("element_code or command are mutually exclusive required")
        if hasattr(command, "data_set_number") and data_set_number is None:
            raise ValueError("command requires data set number")
        if (
            hasattr(command, "programme_service_number")
            and programme_service_number is None
        ):
            raise ValueError("command requires programme service number")

        self._element_code = command.ELEMENT_CODE
        self._dsn = data_set_number
        self._psn = programme_service_number
        self._additional_data = (
            list(additional_data) if additional_data is not None else []
        )

    @property
    def element_code(self) -> int:
        return self._element_code

    @property
    def data_set_number(self) -> int:
        return self._dsn

    @property
    def programme_service_number(self) -> int:
        return self._psn

    def encode(self) -> list[int]:
        request_data = [self._element_code]
        if self._dsn is not None:
            request_data.append(self._dsn)
        if self._psn is not None:
            request_data.append(self._psn)
        if self._additional_data:
            request_data += self._additional_data

        return [self.ELEMENT_CODE, len(request_data)] + request_data

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("RequestCommand", int):
        data = list(data)
        if len(data) < 2:
            raise UECPCommandDecodeNotEnoughData(len(data), 2)
        mec, mel = data[0:2]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        if len(data) < (2 + mel):
            raise UECPCommandDecodeNotEnoughData(len(data), 2 + mel)
        data, idx = data[2:], 0
        element_code, idx = data[idx], idx + 1
        if element_code not in UECPCommand.ELEMENT_CODE_MAP:
            raise ValueError(f"Unknown element code {element_code:#x}")
        command = UECPCommand.ELEMENT_CODE_MAP[element_code]
        data_set_number = None
        if hasattr(command, "data_set_number"):
            data_set_number, idx = data[idx], idx + 1
        programme_service_number = None
        if hasattr(command, "programme_service_number"):
            programme_service_number, idx = data[idx], idx + 1
        additional_data = data[idx:mel]
        return (
            cls(
                command=command,
                data_set_number=data_set_number,
                programme_service_number=programme_service_number,
                additional_data=additional_data,
            ),
            2 + mel,
        )
