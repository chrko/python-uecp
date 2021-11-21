import typing

from uecp.messages.base import UECPMessage
from uecp.messages.mixins import (
    UECPMessageDataSetNumber,
    UECPMessageProgrammeServiceNumber,
)


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
