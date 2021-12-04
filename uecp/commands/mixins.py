from uecp.commands.base import UECPCommandException


class InvalidDataSetNumber(UECPCommandException):
    def __init__(self, data_set_number):
        self.data_set_number = data_set_number

    def __repr__(self) -> str:
        return f"InvalidDataSetNumber(data_set_number={self.data_set_number!r})"

    def __str__(self):
        return (
            f"Supplied an invalid value for data set number. "
            f"Must be an integer between 0x00 and 0xFF. Supplied {self.data_set_number!r}"
        )


class UECPCommandDataSetNumber:
    CURRENT_DATA_SET = 0x00
    ALL_EXCEPT_CURRENT_DATA_SET = 0xFE
    ALL_DATA_SETS = 0xFF

    def __init__(self, data_set_number=0, **kwargs):
        super().__init__(**kwargs)
        self.__data_set_number = 0

        self.data_set_number = data_set_number

    @property
    def data_set_number(self) -> int:
        return self.__data_set_number

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
        self.__data_set_number = new_data_set_number


class InvalidProgrammeServiceNumber(UECPCommandException):
    def __init__(self, programme_service_number):
        self.programme_service_number = programme_service_number

    def __repr__(self) -> str:
        return f"InvalidProgrammeServiceNumber(programme_service_number={self.programme_service_number!r})"

    def __str__(self):
        return (
            f"Supplied an invalid value for programme service number. "
            f"Must be an integer between 0x00 and 0xFF. Supplied {self.programme_service_number!r}"
        )


class UECPCommandProgrammeServiceNumber:
    def __init__(self, programme_service_number=0, **kwargs):
        super().__init__(**kwargs)
        self.__programme_service_number = 0

        self.programme_service_number = programme_service_number

    @property
    def programme_service_number(self) -> int:
        return self.__programme_service_number

    @programme_service_number.setter
    def programme_service_number(self, new_programme_service_number: int):
        try:
            if new_programme_service_number == int(new_programme_service_number):
                new_programme_service_number = int(new_programme_service_number)
            else:
                raise ValueError
        except ValueError:
            raise InvalidProgrammeServiceNumber(new_programme_service_number)

        if not (0x00 <= new_programme_service_number <= 0xFF):
            raise InvalidProgrammeServiceNumber(new_programme_service_number)
        self.__programme_service_number = new_programme_service_number


class UECPCommandDSNnPSN(UECPCommandDataSetNumber, UECPCommandProgrammeServiceNumber):
    pass
