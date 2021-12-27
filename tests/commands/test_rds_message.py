import pytest

from tests.test_utils import from_arcos
from uecp.commands.base import (
    UECPCommandDecodeElementCodeMismatchError,
    UECPCommandDecodeNotEnoughData,
)
from uecp.commands.rds_message import (
    DecoderInformationSetCommand,
    InvalidNumberOfTransmissions,
    ProgrammeIdentificationSetCommand,
    ProgrammeServiceNameSetCommand,
    ProgrammeTypeNameSetCommand,
    ProgrammeTypeSetCommand,
    RadioText,
    RadioTextBufferConfiguration,
    RadioTextSetCommand,
    TrafficAnnouncementProgrammeSetCommand,
)
from uecp.frame import UECPFrameDecoder


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


implicit_carriage_return_warnings = pytest.warns(
    UserWarning,
    match="Implicitly appending a carriage return 0x0D to radio text shorter than 61 characters",
)


class TestRadioText:
    def test_radiotext_validation(self):
        with pytest.raises(UnicodeError), implicit_carriage_return_warnings:
            RadioText(text="\0")

        with pytest.raises(
            InvalidNumberOfTransmissions
        ), implicit_carriage_return_warnings:
            RadioText(text="ABCDE", number_of_transmissions=0x10)

        with pytest.raises(ValueError, match="must not be empty"):
            RadioText(text="")

    def test_carriage_return(self):
        with implicit_carriage_return_warnings:
            rt = RadioText(text="My lovely radio")
            assert rt.text == "My lovely radio\r"

        with implicit_carriage_return_warnings:
            rt.text = "My RADIO is great"
            assert rt.text == "My RADIO is great\r"

        rt = RadioText(
            text="This text is longer than 61 characters and a CR isn't required"
        )
        assert (
            rt.text == "This text is longer than 61 characters and a CR isn't required"
        )


class TestRadioTextSetCommand:
    def test_create_from_1(self):
        """\
        <0A><00><01><04><0B><52><44><53>
        Send to current data set, programme service 1. This message causes the buffer to be
        flushed, the A/B flag to be toggled and the text >RDS< is transmitted indefinitely.
        """
        with implicit_carriage_return_warnings:
            cmd, consumed_bytes = RadioTextSetCommand.create_from(
                [0x0A, 0x00, 0x01, 0x04, 0x0B, 0x52, 0x44, 0x53]
            )  # type: RadioTextSetCommand, int
            assert consumed_bytes == 8
            assert isinstance(cmd, RadioTextSetCommand)
            assert cmd.data_set_number == 0
            assert cmd.programme_service_number == 1
            assert cmd.a_b_toggle is True
            assert (
                cmd.buffer_configuration == RadioTextBufferConfiguration.TRUNCATE_BEFORE
            )
            assert cmd.number_of_transmissions == 5
            assert (
                cmd.text == "RDS\r"
            )  # We enforce appending \r to texts shorter than 61 chars

    def test_create_from_2(self):
        """\
        <0A><00><01><05><51><74><65><78><74>
        Send to current data set, programme service 1. This, message adds another Radiotext
        message >text< to the buffer to be repeated 8 times. The previous message and this
        message are cycled. >RDS< is sent five times, then >text< 8 times and so on."""
        with implicit_carriage_return_warnings:
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
            assert (
                cmd.text == "text\r"
            )  # We enforce appending \r to texts shorter than 61 chars

    def test_complete_frame_setting(self):
        decoder = UECPFrameDecoder()

        data = from_arcos(
            "FE,00,00,03,D3,0A,01,00,39,0A,52,44,53,20,69,73,20,6D,79,20,6C,6F,"
            "76,65,20,6F,6E,20,61,69,72,20,77,69,74,68,20,72,61,64,69,6F,61,6B,"
            "74,69,76,20,2D,20,64,61,73,20,43,61,6D,70,75,73,72,61,64,69,6F,0D,"
            "0A,01,00,0F,47,D9,62,65,6C,73,74,20,67,65,69,6C,20,32,0D,0A,01,00,"
            "3D,52,48,65,75,74,65,20,64,61,62,65,69,0A,4D,61,78,20,4D,99,73,74,"
            "65,72,6D,91,6E,6E,63,68,65,6E,20,6D,69,74,20,56,69,76,69,65,6E,20,"
            "75,6E,64,20,55,6D,6C,61,75,74,65,6E,20,73,61,74,74,0D,0A,01,00,3E,"
            "4C,72,61,64,69,6F,61,6B,74,69,76,20,2D,20,64,65,69,6E,20,43,61,6D,"
            "70,75,73,72,61,64,69,6F,20,61,75,66,20,64,65,72,20,31,30,35,2E,34,"
            "20,4D,48,7A,20,75,6E,64,20,38,39,2E,36,20,4D,48,7A,0D,2D,EC,FF"
        )
        frame, remaining_data = decoder.decode(data)
        assert len(remaining_data) == 0
        assert frame is not None
        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0x03
        assert len(frame.commands) == 4

        cmd = frame.commands[0]  # type: RadioTextSetCommand
        assert cmd.text == "RDS is my love on air with radioaktiv - das Campusradio\r"
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.TRUNCATE_BEFORE
        assert cmd.number_of_transmissions == 5
        assert cmd.a_b_toggle is False
        assert cmd.data_set_number == 1

        cmd = frame.commands[1]  # type: RadioTextSetCommand
        assert cmd.text == "Übelst geil 2\r"
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.APPEND
        assert cmd.number_of_transmissions == 3
        assert cmd.a_b_toggle is True
        assert cmd.data_set_number == 1

        cmd = frame.commands[2]  # type: RadioTextSetCommand
        assert (
            cmd.text == "Heute dabei\nMax Müstermännchen mit Vivien und Umlauten satt\r"
        )

        cmd = frame.commands[3]  # type: RadioTextSetCommand
        assert (
            cmd.text == "radioaktiv - dein Campusradio auf der 105.4 MHz und 89.6 MHz\r"
        )

        data = from_arcos(
            "FE,00,00,04,FA,0A,01,00,3F,4B,5A,75,6D,20,53,63,68,6C,75,73,73,20,"
            "6E,6F,63,68,20,65,69,6E,20,70,61,61,72,20,57,6F,72,74,65,20,69,6E,"
            "20,64,69,65,20,52,75,6E,64,65,2C,20,62,65,76,6F,72,20,65,73,20,7A,"
            "75,20,45,6E,64,65,0A,01,00,3E,48,46,61,73,74,20,62,69,6E,20,69,63,"
            "68,20,64,75,72,63,68,20,6D,69,74,20,64,65,6E,20,54,65,73,74,64,61,"
            "74,65,6E,2C,20,68,6F,66,66,65,6E,74,6C,69,63,68,20,67,65,68,74,20,"
            "65,73,20,6E,75,6E,0A,01,00,3E,48,57,6F,68,6C,20,6D,97,67,6C,69,63,"
            "68,20,61,62,65,72,20,6C,65,69,64,65,72,20,77,65,69,74,65,72,68,69,"
            "6E,20,6E,69,63,68,74,20,3A,28,20,44,61,73,20,77,91,72,65,20,73,63,"
            "68,61,64,65,21,0D,0A,01,00,2F,46,4D,65,69,6E,20,6C,65,74,7A,65,72,"
            "20,52,61,64,69,6F,54,65,78,74,20,66,99,72,20,68,65,75,74,65,2C,20,"
            "68,6F,66,66,65,6E,74,6C,69,63,68,21,0D,8D,33,FF"
        )

        frame, remaining_data = decoder.decode(data)
        assert len(remaining_data) == 0
        assert frame is not None
        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0x04
        assert len(frame.commands) == 4

        cmd = frame.commands[0]  # type: RadioTextSetCommand
        assert (
            cmd.text == "Zum Schluss noch ein paar Worte in die Runde, bevor es zu Ende"
        )
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.APPEND
        assert cmd.number_of_transmissions == 5
        assert cmd.a_b_toggle is True
        assert cmd.data_set_number == 1

        cmd = frame.commands[1]  # type: RadioTextSetCommand
        assert (
            cmd.text == "Fast bin ich durch mit den Testdaten, hoffentlich geht es nun"
        )
        assert cmd.buffer_configuration == RadioTextBufferConfiguration.APPEND
        assert cmd.number_of_transmissions == 4
        assert cmd.a_b_toggle is False
        assert cmd.data_set_number == 1

        cmd = frame.commands[2]  # type: RadioTextSetCommand
        assert (
            cmd.text == "Wohl möglich aber leider weiterhin nicht :( Das wäre schade!\r"
        )

        cmd = frame.commands[3]  # type: RadioTextSetCommand
        assert cmd.text == "Mein letzer RadioText für heute, hoffentlich!\r"
