import abc
import typing


class UECPMessage(abc.ABC):
    ELEMENT_CODE = ...
    ELEMENT_CODE_MAP: dict[int, "UECPMessage"] = {}

    @abc.abstractmethod
    def encode(self) -> list[int]:
        ...

    @classmethod
    @abc.abstractmethod
    def create_from(cls, data: typing.Union[bytes, list[int]]) -> ("UECPMessage", int):
        ...

    @classmethod
    def register_type(cls, message_type: "UECPMessage") -> "UECPMessage":
        mec = int(message_type.ELEMENT_CODE)
        if not (0x01 <= mec <= 0xFD):
            raise ValueError(f"MEC must be in [0x01, 0xFD], given {mec:#x}")
        if mec in cls.ELEMENT_CODE_MAP:
            raise ValueError(f"MEC {mec:#x} already defined")
        cls.ELEMENT_CODE_MAP[mec] = message_type
        return message_type

    @classmethod
    def decode_messages(cls, data: typing.Union[bytes, list[int]]) -> ["UECPMessage"]:
        msgs = []
        data = list(data)
        while len(data) > 0:
            mec = data[0]
            if mec not in cls.ELEMENT_CODE_MAP:
                raise ValueError()
            msg, consumed_bytes = cls.ELEMENT_CODE_MAP[mec].create_from(data)
            msgs.append(msg)
            data = data[consumed_bytes:]
        return msgs
