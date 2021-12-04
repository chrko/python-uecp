import abc
import typing


class UECPCommand(abc.ABC):
    ELEMENT_CODE = ...
    ELEMENT_CODE_MAP: dict[int, "UECPCommand"] = {}

    @abc.abstractmethod
    def encode(self) -> list[int]:
        ...

    @classmethod
    @abc.abstractmethod
    def create_from(cls, data: typing.Union[bytes, list[int]]) -> ("UECPCommand", int):
        ...

    @classmethod
    def register_type(cls, message_type: "UECPCommand") -> "UECPCommand":
        mec = int(message_type.ELEMENT_CODE)
        if not (0x01 <= mec <= 0xFD):
            raise ValueError(f"MEC must be in [0x01, 0xFD], given {mec:#x}")
        if mec in cls.ELEMENT_CODE_MAP:
            raise ValueError(f"MEC {mec:#x} already defined")
        cls.ELEMENT_CODE_MAP[mec] = message_type
        return message_type

    @classmethod
    def decode_commands(cls, data: typing.Union[bytes, list[int]]) -> ["UECPCommand"]:
        cmds = []
        data = list(data)
        while len(data) > 0:
            mec = data[0]
            if mec not in cls.ELEMENT_CODE_MAP:
                raise ValueError()
            cmd, consumed_bytes = cls.ELEMENT_CODE_MAP[mec].create_from(data)
            cmds.append(cmd)
            data = data[consumed_bytes:]
        return cmds


class UECPCommandException(Exception):
    pass


class UECPCommandDecodeError(UECPCommandException):
    pass


class UECPCommandDecodeNotEnoughData(UECPCommandDecodeError):
    pass


class UECPCommandDecodeElementCodeMismatchError(UECPCommandDecodeError):
    pass
