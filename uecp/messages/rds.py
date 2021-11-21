import typing

from uecp.messages.base import UECPMessage
from uecp.messages.mixins import UECPMessageDSNnPSN


@UECPMessage.register_type
class ProgrammeIdentificationMessage(UECPMessage, UECPMessageDSNnPSN):
    ELEMENT_CODE = 0x01

    def __init__(self, pi=0, data_set_number=0, programme_service_number=0):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__pi = 0
        self.pi = pi

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
            self.__pi >> 8,
            self.__pi & 0xFF,
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
        return self.__pi

    @pi.setter
    def pi(self, new_pi: int):
        if not (0x00 <= new_pi <= 0xFFFF):
            raise ValueError()
        self.__pi = new_pi


class InvalidProgrammeServiceName(ValueError):
    def __init__(self, programme_service_name, cause: str = "unknown"):
        self.programme_service_name = programme_service_name
        self.cause = str(cause)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(programme_service_name={self.programme_service_name!r}, cause={self.cause!r})"

    def __str__(self):
        return f"Supplied an invalid value for programme service name, cause: {self.cause}. Supplied {self.programme_service_name!r}"


@UECPMessage.register_type
class ProgrammeServiceNameMessage(UECPMessage, UECPMessageDSNnPSN):
    ELEMENT_CODE = 0x02

    def __init__(self, ps: str = "", data_set_number=0, programme_service_number=0):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__ps = ""
        self.ps = ps

    @property
    def ps(self) -> str:
        return self.__ps

    @ps.setter
    def ps(self, new_ps: str):
        new_ps = str(new_ps)
        if len(new_ps) > 8:
            raise InvalidProgrammeServiceName(new_ps, f"PS supports only 8 characters")
        new_ps = new_ps.rstrip(" ")
        try:
            new_ps.encode("basic_rds_character_set")
        except ValueError as e:
            raise InvalidProgrammeServiceName(
                new_ps, f"PS cannot be encoded, exc={e!r}"
            )
        self.__ps = new_ps

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
        ] + list(self.__ps.ljust(8).encode("basic_rds_character_set"))

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> ("ProgrammeServiceNameMessage", int):
        data = list(data)
        if len(data) < 11:
            raise ValueError()

        mec, dsn, psn = data[0:3]
        if mec != cls.ELEMENT_CODE:
            raise ValueError()

        ps = bytes(data[3:11]).decode("basic_rds_character_set")

        return cls(ps=ps, data_set_number=dsn, programme_service_number=psn), 11
