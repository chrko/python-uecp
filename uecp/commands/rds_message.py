import enum
import typing
import warnings

import attr

from uecp.commands.base import (
    UECPCommand,
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
    UECPCommandException,
)
from uecp.commands.mixins import UECPCommandDSNnPSN


# PIN 0x06 / Programme Item Number not implemented as deprecated
# MS 0x05 / Music/Speech flag deprecated


class InvalidProgrammeIdentification(UECPCommandException):
    pass


@UECPCommand.register_type
class ProgrammeIdentificationSetCommand(UECPCommand, UECPCommandDSNnPSN):
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
    ) -> tuple["ProgrammeIdentificationSetCommand", int]:
        data = list(data)
        if len(data) < 5:
            raise UECPCommandDecodeNotEnoughData(len(data), 5)

        mec, dsn, psn, pi_msb, pi_lsb = data[0:5]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        pi = pi_msb << 8 | pi_lsb

        return cls(pi=pi, data_set_number=dsn, programme_service_number=psn), 5

    @property
    def pi(self) -> int:
        return self.__pi

    @pi.setter
    def pi(self, new_pi: int):
        try:
            if new_pi == int(new_pi):
                new_pi = int(new_pi)
            else:
                raise ValueError()
        except ValueError:
            raise InvalidProgrammeIdentification(new_pi)

        if not (0x0 <= new_pi <= 0xFFFF):
            raise InvalidProgrammeIdentification(new_pi)
        self.__pi = new_pi


class InvalidProgrammeServiceName(UECPCommandException):
    def __init__(self, programme_service_name, cause: str = "unknown"):
        self.programme_service_name = programme_service_name
        self.cause = str(cause)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(programme_service_name={self.programme_service_name!r}, cause={self.cause!r})"

    def __str__(self):
        return f"Supplied an invalid value for programme service name, cause: {self.cause}. Supplied {self.programme_service_name!r}"


@UECPCommand.register_type
class ProgrammeServiceNameSetCommand(UECPCommand, UECPCommandDSNnPSN):
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
    ) -> tuple["ProgrammeServiceNameSetCommand", int]:
        data = list(data)
        if len(data) < 11:
            raise UECPCommandDecodeNotEnoughData(len(data), 11)

        mec, dsn, psn = data[0:3]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        ps = bytes(data[3:11]).decode("basic_rds_character_set")

        return cls(ps=ps, data_set_number=dsn, programme_service_number=psn), 11


@UECPCommand.register_type
class DecoderInformationSetCommand(UECPCommand, UECPCommandDSNnPSN):
    ELEMENT_CODE = 0x04

    def __init__(
        self,
        stereo=False,
        dynamic_pty=False,
        data_set_number=0,
        programme_service_number=0,
    ):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__stereo = bool(stereo)
        self.__dynamic_pty = bool(dynamic_pty)
        # artificial head & compressed deprecated; stereo / mono flagged to be checked

    @property
    def stereo(self) -> bool:
        return self.__stereo

    @stereo.setter
    def stereo(self, enabled: bool):
        self.__stereo = bool(enabled)

    @property
    def mono(self) -> bool:
        return not self.__stereo

    @mono.setter
    def mono(self, enabled: bool):
        self.__stereo = not bool(enabled)

    @property
    def dynamic_pty(self) -> bool:
        return self.__dynamic_pty

    @dynamic_pty.setter
    def dynamic_pty(self, enabled: bool):
        self.__dynamic_pty = bool(enabled)

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
            self.__dynamic_pty << 3 | self.__stereo,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> tuple["DecoderInformationSetCommand", int]:
        data = list(data)
        if len(data) < 4:
            raise UECPCommandDecodeNotEnoughData(len(data), 4)

        mec, dsn, psn, flags = data[0:4]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        stereo = 0b1 & flags
        dynamic_pty = 0b1000 & flags

        return (
            cls(
                stereo=stereo,
                dynamic_pty=dynamic_pty,
                data_set_number=dsn,
                programme_service_number=psn,
            ),
            4,
        )


@UECPCommand.register_type
class TrafficAnnouncementProgrammeSetCommand(UECPCommand, UECPCommandDSNnPSN):
    ELEMENT_CODE = 0x03

    def __init__(
        self,
        announcement=False,
        programme=False,
        data_set_number=0,
        programme_service_number=0,
    ):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__announcement = bool(announcement)
        self.__programme = bool(programme)

    @property
    def announcement(self) -> bool:
        return self.__announcement

    @announcement.setter
    def announcement(self, enabled: bool):
        self.__announcement = bool(enabled)

    @property
    def programme(self):
        return self.__programme

    @programme.setter
    def programme(self, enabled: bool):
        self.__programme = bool(enabled)

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
            self.__programme << 1 | self.__announcement,
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> tuple["TrafficAnnouncementProgrammeSetCommand", int]:
        data = list(data)
        if len(data) < 4:
            raise UECPCommandDecodeNotEnoughData(len(data), 4)

        mec, dsn, psn, flags = data[0:4]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        announcement = 0b1 & flags
        programme = 0b10 & flags

        return (
            cls(
                announcement=announcement,
                programme=programme,
                data_set_number=dsn,
                programme_service_number=psn,
            ),
            4,
        )


@enum.unique
class ProgrammeType(enum.IntEnum):
    UNDEFINED = 0
    NEWS = 1
    CURRENT_AFFAIRS = 2
    INFORMATION = 3
    SPORT = 4
    EDUCATION = 5
    DRAMA = 6
    CULTURE = 7
    SCIENCE = 8
    VARIED = 9
    POP_MUSIC = 10
    ROCK_MUSIC = 11
    EASY_LISTENING_MUSIC = 12
    LIGHT_CLASSICAL = 13
    SERIOUS_CLASSICAL = 14
    OTHER_MUSIC = 15
    WEATHER = 16
    FINANCE = 17
    CHILDREN_PROGRAMME = 18
    SOCIAL_AFFAIRS = 19
    RELIGION = 20
    PHONE_IN = 21
    TRAVEL = 22
    LEISURE = 23
    JAZZ_MUSIC = 24
    COUNTRY_MUSIC = 25
    NATIONAL_MUSIC = 26
    OLDIES_MUSIC = 27
    FOLK_MUSIC = 28
    DOCUMENTARY = 29
    ALARM_TEST = 30
    ALARM = 31


@UECPCommand.register_type
class ProgrammeTypeSetCommand(UECPCommand, UECPCommandDSNnPSN):
    ELEMENT_CODE = 0x07

    def __init__(
        self,
        programme_type: typing.Union[ProgrammeType, int] = ProgrammeType.UNDEFINED,
        data_set_number=0,
        programme_service_number=0,
    ):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__programme_type = ProgrammeType(programme_type)

    @property
    def programme_type(self) -> ProgrammeType:
        return self.__programme_type

    @programme_type.setter
    def programme_type(self, new_programme_type: typing.Union[int, ProgrammeType]):
        self.__programme_type = ProgrammeType(new_programme_type)

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
            int(self.__programme_type),
        ]

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> tuple["ProgrammeTypeSetCommand", int]:
        data = list(data)
        if len(data) < 4:
            raise UECPCommandDecodeNotEnoughData(len(data), 4)

        mec, dsn, psn, programme_type = data[0:4]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        programme_type = ProgrammeType(programme_type)

        return (
            cls(
                programme_type=programme_type,
                data_set_number=dsn,
                programme_service_number=psn,
            ),
            4,
        )


class InvalidProgrammeTypeName(UECPCommandException):
    def __init__(self, programme_type_name, cause: str = "unknown"):
        self.programme_type_name = programme_type_name
        self.cause = str(cause)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(programme_type_name={self.programme_type_name!r}, cause={self.cause!r})"

    def __str__(self):
        return f"Supplied an invalid value for programme type name, cause: {self.cause}. Supplied {self.programme_type_name!r}"


@UECPCommand.register_type
class ProgrammeTypeNameSetCommand(UECPCommand, UECPCommandDSNnPSN):
    ELEMENT_CODE = 0x3E

    def __init__(
        self, programme_type_name="", data_set_number=0, programme_service_number=0
    ):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        self.__programme_type_name = ""
        self.programme_type_name = programme_type_name

    @property
    def programme_type_name(self) -> str:
        return self.__programme_type_name

    @programme_type_name.setter
    def programme_type_name(self, new_programme_type_name: str):
        new_programme_type_name = str(new_programme_type_name)
        if len(new_programme_type_name) > 8:
            raise InvalidProgrammeTypeName(
                new_programme_type_name, f"PTYN supports only 8 characters"
            )
        new_programme_type_name = new_programme_type_name.rstrip(" ")
        try:
            new_programme_type_name.encode("basic_rds_character_set")
        except ValueError as e:
            raise InvalidProgrammeServiceName(
                new_programme_type_name, f"PTYN cannot be encoded, exc={e!r}"
            )
        self.__programme_type_name = new_programme_type_name

    def encode(self) -> list[int]:
        return [
            self.ELEMENT_CODE,
            self.data_set_number,
            self.programme_service_number,
        ] + list(self.__programme_type_name.ljust(8).encode("basic_rds_character_set"))

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> tuple["ProgrammeTypeNameSetCommand", int]:
        data = list(data)
        if len(data) < 11:
            raise UECPCommandDecodeNotEnoughData(len(data), 11)

        mec, dsn, psn = data[0:3]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)

        programme_type_name = bytes(data[3:11]).decode("basic_rds_character_set")

        return (
            cls(
                programme_type_name=programme_type_name,
                data_set_number=dsn,
                programme_service_number=psn,
            ),
            11,
        )


@enum.unique
class RadioTextBufferConfiguration(enum.IntEnum):
    TRUNCATE_BEFORE = 0b00
    APPEND = 0b10


class InvalidNumberOfTransmissions(UECPCommandException):
    pass


def _ensure_radio_text_carriage_return(*values: str) -> str:
    if len(values) < 1:
        import inspect

        raise TypeError(
            f"{inspect.stack()[0][3]} must be called with at least one argument and the last one must be a string"
        )
    value = values[-1]
    value = str(value)
    if 0 < len(value) < 61 and value[-1] != "\r":
        value += "\r"
        warnings.warn(
            "Implicitly appending a carriage return 0x0D to radio text shorter than 61 characters"
        )
    return value


def _check_radio_text(_, __, value: str):
    value = str(value)
    if len(value) > 64 or len(value) == 0:
        raise ValueError(
            f"Radio text supports only up to 64 characters and must not be empty, given {value!r}",
        )
    if len(value) < 61 and value[-1] != "\r":
        raise ValueError(
            f"Radio text shorter than 61 characters must be terminated by a carriage return, given {value!r}"
        )
    value.encode("basic_rds_character_set")

    return value


@attr.s
class RadioText:
    text: str = attr.ib(
        converter=_ensure_radio_text_carriage_return,
        validator=_check_radio_text,
        on_setattr=[
            _ensure_radio_text_carriage_return,  # type:ignore
            _check_radio_text,
        ],
    )
    number_of_transmissions: int = attr.ib(default=0, converter=int)
    a_b_toggle: bool = attr.ib(default=False, converter=bool)

    @number_of_transmissions.validator
    def _check_number_of_transmissions(self, _, new_not: int):
        if not (0x0 <= new_not <= 0xF):
            raise InvalidNumberOfTransmissions(new_not)


@UECPCommand.register_type
class RadioTextSetCommand(UECPCommand, UECPCommandDSNnPSN):
    ELEMENT_CODE = 0x0A
    INFINITE_TRANSMISSIONS = 0

    def __init__(
        self,
        text="",
        number_of_transmissions=0,
        a_b_toggle=False,
        buffer_configuration=RadioTextBufferConfiguration.TRUNCATE_BEFORE,
        data_set_number=0,
        programme_service_number=0,
        radiotext: RadioText = None,
    ):
        super().__init__(
            data_set_number=data_set_number,
            programme_service_number=programme_service_number,
        )
        if radiotext is not None:
            self._radiotext = radiotext
        else:
            self._radiotext = RadioText(
                text=text,
                number_of_transmissions=number_of_transmissions,
                a_b_toggle=a_b_toggle,
            )
        self._buffer_configuration = RadioTextBufferConfiguration(buffer_configuration)

    @property
    def text(self) -> str:
        return self._radiotext.text

    @text.setter
    def text(self, new_text: str):
        self._radiotext.text = new_text

    @property
    def number_of_transmissions(self) -> int:
        return self._radiotext.number_of_transmissions

    @number_of_transmissions.setter
    def number_of_transmissions(self, new_not: int):
        self._radiotext.number_of_transmissions = new_not

    @property
    def a_b_toggle(self) -> bool:
        return self._radiotext.a_b_toggle

    @a_b_toggle.setter
    def a_b_toggle(self, toggle: bool):
        self._radiotext.a_b_toggle = toggle

    @property
    def buffer_configuration(self) -> RadioTextBufferConfiguration:
        return self._buffer_configuration

    @buffer_configuration.setter
    def buffer_configuration(self, buffer_conf: RadioTextBufferConfiguration):
        self._buffer_configuration = RadioTextBufferConfiguration(buffer_conf)

    @property
    def radiotext(self) -> RadioText:
        return self._radiotext

    def encode(self) -> list[int]:
        data = [self.ELEMENT_CODE, self.data_set_number, self.programme_service_number]
        if (
            len(self._radiotext.text) == 0
            and self._buffer_configuration
            is RadioTextBufferConfiguration.TRUNCATE_BEFORE
        ):
            data.append(0)
        else:
            mel = 1 + len(self._radiotext.text)
            flags = (
                self._buffer_configuration << 5
                | self._radiotext.number_of_transmissions << 1
                | self._radiotext.a_b_toggle
            )
            data += [mel, flags]
            data += list(self._radiotext.text.encode("basic_rds_character_set"))
        return data

    @classmethod
    def create_from(
        cls, data: typing.Union[bytes, list[int]]
    ) -> tuple["RadioTextSetCommand", int]:
        data = list(data)
        if len(data) < 4:
            raise UECPCommandDecodeNotEnoughData(len(data), 4)
        mec, dsn, psn, mel = data[0:4]
        if mec != cls.ELEMENT_CODE:
            raise UECPCommandDecodeElementCodeMismatchError(mec, cls.ELEMENT_CODE)
        if mel == 0:
            return cls(data_set_number=0, programme_service_number=0), 4
        data = data[4:]
        if len(data) < mel:
            raise UECPCommandDecodeNotEnoughData(len(data), mel)
        flags = data[0]
        buffer_configuration = (flags & 0b0110_0000) >> 5
        number_of_transmission = (flags & 0b0001_1110) >> 1
        a_b_toggle = flags & 0b0000_0001
        text_data = bytes(data[1:mel])
        text = text_data.decode("basic_rds_character_set")

        return (
            cls(
                text=text,
                buffer_configuration=buffer_configuration,
                number_of_transmissions=number_of_transmission,
                a_b_toggle=a_b_toggle,
                data_set_number=dsn,
                programme_service_number=psn,
            ),
            4 + mel,
        )


# TODO AF
# TODO EON-AF
# TODO Slow Labeling Codes
# TODO Linkage information
