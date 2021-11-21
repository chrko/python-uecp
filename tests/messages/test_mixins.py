import pytest

from uecp.messages.mixins import (
    InvalidDataSetNumber,
    InvalidProgrammeServiceNumber,
    UECPMessageDataSetNumber,
    UECPMessageProgrammeServiceNumber,
)


class TestMixins:
    @pytest.mark.parametrize(
        "cls, exception",
        [
            (UECPMessageDataSetNumber, InvalidDataSetNumber),
            (UECPMessageProgrammeServiceNumber, InvalidProgrammeServiceNumber),
        ],
    )
    @pytest.mark.parametrize("value", [0.5, "a string", -4])
    def test_invalid_dsn(self, cls, exception, value):
        with pytest.raises(exception):
            cls(value)
