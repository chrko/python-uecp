import pytest

from uecp.messages.base import (
    UECPMessageDecodeElementCodeMismatchError,
    UECPMessageDecodeNotEnoughData,
)
from uecp.messages.rds import (
    DecoderInformationMessage,
    ProgrammeIdentificationMessage,
    ProgrammeServiceNameMessage,
    ProgrammeTypeMessage,
    ProgrammeTypeNameMessage,
    TrafficAnnouncementProgrammeMessage,
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

        with pytest.raises(UECPMessageDecodeNotEnoughData):
            ProgrammeIdentificationMessage.create_from([0x01])

        with pytest.raises(UECPMessageDecodeElementCodeMismatchError):
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


class TestDIMessage:
    def test_encoding(self):
        msg = DecoderInformationMessage(stereo=True, programme_service_number=3)
        assert msg.encode() == [0x04, 0x00, 0x03, 0x01]

    def test_create_from(self):
        msg, consumed_bytes = DecoderInformationMessage.create_from(
            [0x04, 0x00, 0x03, 0x01]
        )
        assert consumed_bytes == 4
        assert msg.data_set_number == 0
        assert msg.programme_service_number == 3
        assert msg.stereo is True
        assert msg.dynamic_pty is False


class TestTATPMessage:
    def test_encoding(self):
        msg = TrafficAnnouncementProgrammeMessage(
            programme=True,
            announcement=False,
            data_set_number=0,
            programme_service_number=5,
        )
        assert msg.encode() == [0x03, 0x00, 0x05, 0x02]

    def test_create_from(self):
        msg, consumed_bytes = TrafficAnnouncementProgrammeMessage.create_from(
            [0x03, 0x00, 0x05, 0x02]
        )
        assert consumed_bytes == 4
        assert msg.data_set_number == 0
        assert msg.programme_service_number == 5
        assert msg.announcement is False
        assert msg.programme is True


class TestPTYMessage:
    def test_encoding(self):
        msg = ProgrammeTypeMessage(
            programme_type=8, data_set_number=0, programme_service_number=5
        )
        assert msg.encode() == [0x07, 0x00, 0x05, 0x08]

    def test_create_from(self):
        msg, consumed_bytes = ProgrammeTypeMessage.create_from([0x07, 0x00, 0x05, 0x08])
        assert consumed_bytes == 4
        assert msg.programme_type == 8
        assert msg.data_set_number == 0
        assert msg.programme_service_number == 5


class TestPTYNMessage:
    def test_encoding(self):
        msg = ProgrammeTypeNameMessage(
            data_set_number=0,
            programme_service_number=2,
            programme_type_name="Football",
        )
        assert msg.encode() == [
            0x3E,
            0x00,
            0x02,
            0x46,
            0x6F,
            0x6F,
            0x74,
            0x62,
            0x61,
            0x6C,
            0x6C,
        ]

    def test_create_from(self):
        msg, consumed_bytes = ProgrammeTypeNameMessage.create_from(
            [
                0x3E,
                0x00,
                0x02,
                0x46,
                0x6F,
                0x6F,
                0x74,
                0x62,
                0x61,
                0x6C,
                0x6C,
            ]
        )
        assert consumed_bytes == 11
        assert msg.programme_service_number == 2
        assert msg.data_set_number == 0
        assert msg.programme_type_name == "Football"
