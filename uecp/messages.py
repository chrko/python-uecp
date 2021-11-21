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
        if mec in cls.ELEMENT_CODE_MAP:
            raise ValueError()
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


class UECPMessageDataSetNumber:
    def __init__(self, data_set_number=0, **kwargs):
        super().__init__(**kwargs)
        self._data_set_number = 0

        self.data_set_number = data_set_number

    @property
    def data_set_number(self) -> int:
        return self._data_set_number

    @data_set_number.setter
    def data_set_number(self, new_data_set_number: int):
        if not (0x00 <= new_data_set_number <= 0xFF):
            raise ValueError()
        self._data_set_number = new_data_set_number


class UECPMessageProgrammeServiceNumber:
    def __init__(self, programme_service_number=0, **kwargs):
        super().__init__(**kwargs)
        self._programme_service_number = 0

        self.programme_service_number = programme_service_number

    @property
    def programme_service_number(self) -> int:
        return self._programme_service_number

    @programme_service_number.setter
    def programme_service_number(self, new_programme_service_number: int):
        if not (0x00 <= new_programme_service_number <= 0xFF):
            raise ValueError()
        self._programme_service_number = new_programme_service_number


@UECPMessage.register_type
class ProgrammeIdentificationMessage(
    UECPMessage, UECPMessageDataSetNumber, UECPMessageProgrammeServiceNumber
):
    ELEMENT_CODE = 0x01

    def __init__(self, pi=0, data_set_number=0, programme_service_number=0):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self._pi = 0
        self.pi = pi

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
            self._pi >> 8,
            self._pi & 0xFF,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("ProgrammeIdentificationMessage", int):
        data = list(data)
        if len(data) < 5:
            raise ValueError()

        mec, dsn, psn, pi_msb, pi_lsb = data[0:5]
        if mec != cls.ELEMENT_CODE:
            raise ValueError()

        pi = pi_msb << 8 | pi_lsb

        return cls(pi=pi, data_set_number=dsn, programme_service_number=psn), 5

    @property
    def pi(self) -> int:
        return self._pi

    @pi.setter
    def pi(self, new_pi: int):
        if not (0x00 <= new_pi <= 0xFFFF):
            raise ValueError()
        self._pi = new_pi
