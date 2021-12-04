import pytest

from uecp.commands.base import (
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)
from uecp.commands.rds_message import (
    DecoderInformationSetCommand,
    ProgrammeIdentificationSetCommand,
    ProgrammeServiceNameSetCommand,
    ProgrammeTypeNameSetCommand,
    ProgrammeTypeSetCommand,
    RadioTextBufferConfiguration,
    RadioTextSetCommand,
    TrafficAnnouncementProgrammeSetCommand,
)


class TestPISetCommand:
    def test_encoding(self):
        cmd = ProgrammeIdentificationSetCommand(
            pi=0xABCD, data_set_number=0x3F, programme_service_number=0xDA
        )
        assert cmd.encode() == [0x01, 0x3F, 0xDA, 0xAB, 0xCD]

    def test_create_from(self):
        cmd, consumed_bytes = ProgrammeIdentificationSetCommand.create_from(
            [0x01, 0x3F, 0xDA, 0xAB, 0xCD]
        )
        assert cmd.pi == 0xABCD
        assert cmd.programme_service_number == 0xDA
        assert cmd.data_set_number == 0x3F
        assert consumed_bytes == 5

        with pytest.raises(UECPCommandDecodeNotEnoughData):
            ProgrammeIdentificationSetCommand.create_from([0x01])

        with pytest.raises(UECPCommandDecodeElementCodeMismatchError):
            ProgrammeIdentificationSetCommand.create_from(
                [0xF1, 0x02, 0x03, 0x04, 0x05]
            )


class TestPSSetCommand:
    def test_encoding(self):
        cmd = ProgrammeServiceNameSetCommand(
            ps="RADIO 1", data_set_number=0, programme_service_number=2
        )
        assert cmd.encode() == [
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
        cmd, consumed_bytes = ProgrammeServiceNameSetCommand.create_from(
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
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 2
        assert cmd.ps == "RADIO 1"


class TestDISetCommand:
    def test_encoding(self):
        cmd = DecoderInformationSetCommand(stereo=True, programme_service_number=3)
        assert cmd.encode() == [0x04, 0x00, 0x03, 0x01]

    def test_create_from(self):
        cmd, consumed_bytes = DecoderInformationSetCommand.create_from(
            [0x04, 0x00, 0x03, 0x01]
        )
        assert consumed_bytes == 4
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 3
        assert cmd.stereo is True
        assert cmd.dynamic_pty is False


class TestTATPSetCommand:
    def test_encoding(self):
        cmd = TrafficAnnouncementProgrammeSetCommand(
            programme=True,
            announcement=False,
            data_set_number=0,
            programme_service_number=5,
        )
        assert cmd.encode() == [0x03, 0x00, 0x05, 0x02]

    def test_create_from(self):
        cmd, consumed_bytes = TrafficAnnouncementProgrammeSetCommand.create_from(
            [0x03, 0x00, 0x05, 0x02]
        )
        assert consumed_bytes == 4
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 5
        assert cmd.announcement is False
        assert cmd.programme is True


class TestPTYSetCommand:
    def test_encoding(self):
        cmd = ProgrammeTypeSetCommand(
            programme_type=8, data_set_number=0, programme_service_number=5
        )
        assert cmd.encode() == [0x07, 0x00, 0x05, 0x08]

    def test_create_from(self):
        cmd, consumed_bytes = ProgrammeTypeSetCommand.create_from(
            [0x07, 0x00, 0x05, 0x08]
        )
        assert consumed_bytes == 4
        assert cmd.programme_type == 8
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 5


class TestPTYNSetCommand:
    def test_encoding(self):
        cmd = ProgrammeTypeNameSetCommand(
            data_set_number=0,
            programme_service_number=2,
            programme_type_name="Football",
        )
        assert cmd.encode() == [
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
        cmd, consumed_bytes = ProgrammeTypeNameSetCommand.create_from(
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
        assert cmd.programme_service_number == 2
        assert cmd.data_set_number == 0
        assert cmd.programme_type_name == "Football"


class TestRadioTextSetCommand:
    def test_create_from_1(self):
        """\
        <0A><00><01><04><0B><52><44><53>
        Send to current data set, programme service 1. This message causes the buffer to be
        flushed, the A/B flag to be toggled and the text >RDS< is transmitted indefinitely.
        """
        cmd, consumed_bytes = RadioTextSetCommand.create_from(
            [0x0A, 0x00, 0x01, 0x04, 0x0B, 0x52, 0x44, 0x53]
        )  # type: RadioTextSetCommand, int
        assert consumed_bytes == 8
        assert isinstance(cmd, RadioTextSetCommand)
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 1
        assert cmd.a_b_toggle is True
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.TRUNCATE_BEFORE
        assert cmd.number_of_transmissions == 5
        assert cmd.text == "RDS"

    def test_create_from_2(self):
        """\
        <0A><00><01><05><51><74><65><78><74>
        Send to current data set, programme service 1. This, message adds another Radiotext
        message >text< to the buffer to be repeated 8 times. The previous message and this
        message are cycled. >RDS< is sent five times, then >text< 8 times and so on."""

        cmd, consumed_bytes = RadioTextSetCommand.create_from(
            [0x0A, 0x00, 0x01, 0x05, 0x51, 0x74, 0x65, 0x78, 0x74]
        )  # type: RadioTextSetCommand, int

        assert consumed_bytes == 9
        assert isinstance(cmd, RadioTextSetCommand)
        assert cmd.data_set_number == 0
        assert cmd.programme_service_number == 1
        assert cmd.a_b_toggle is True
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.APPEND
        assert cmd.number_of_transmissions == 8
        assert cmd.text == "text"
