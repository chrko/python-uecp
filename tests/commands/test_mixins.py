import pytest

from uecp.commands.mixins import (
    InvalidDataSetNumber,
    InvalidProgrammeServiceNumber,
    UECPCommandDataSetNumber,
    UECPCommandProgrammeServiceNumber,
)


class TestMixins:
    @pytest.mark.parametrize(
        "cls, exception",
        [
            (UECPCommandDataSetNumber, InvalidDataSetNumber),
            (UECPCommandProgrammeServiceNumber, InvalidProgrammeServiceNumber),
        ],
    )
    @pytest.mark.parametrize("value", [0.5, "a string", -4])
    def test_invalid_dsn(self, cls, exception, value):
        with pytest.raises(exception):
            cls(value)
