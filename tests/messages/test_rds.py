import pytest

from uecp.messages.rds import (
    ProgrammeIdentificationMessage,
    ProgrammeServiceNameMessage,
)


class TestPIMessage:
    def test_encoding(self):
        msg = ProgrammeIdentificationMessage(
            pi=0xABCD, data_set_number=0x3F, programme_service_number=0xDA
        )
        assert msg.encode() == [0x01, 0x3F, 0xDA, 0xAB, 0xCD]

    def test_create_from(self):
        msg, consumed_bytes = ProgrammeIdentificationMessage.create_from(
            [0x01, 0x3F, 0xDA, 0xAB, 0xCD]
        )
        assert msg.pi == 0xABCD
        assert msg.programme_service_number == 0xDA
        assert msg.data_set_number == 0x3F
        assert consumed_bytes == 5

        with pytest.raises(ValueError):
            ProgrammeIdentificationMessage.create_from([0x01])

        with pytest.raises(ValueError):
            ProgrammeIdentificationMessage.create_from([0xF1, 0x02, 0x03, 0x04, 0x05])


class TestPSMessage:
    def test_encoding(self):
        msg = ProgrammeServiceNameMessage(
            ps="RADIO 1", data_set_number=0, programme_service_number=2
        )
        assert msg.encode() == [
            0x02,
            0x00,
            0x02,
            0x52,
            0x41,
            0x44,
            0x49,
            0x4F,
            0x20,
            0x31,
            0x20,
        ]

    def test_create_from(self):
        msg, consumed_bytes = ProgrammeServiceNameMessage.create_from(
            [
                0x02,
                0x00,
                0x02,
                0x52,
                0x41,
                0x44,
                0x49,
                0x4F,
                0x20,
                0x31,
                0x20,
            ]
        )
        assert consumed_bytes == 11
        assert msg.data_set_number == 0
        assert msg.programme_service_number == 2
        assert msg.ps == "RADIO 1"
