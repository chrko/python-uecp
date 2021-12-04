from uecp.commands.base import UECPCommand
from uecp.commands.rds_message import (
    ProgrammeIdentificationSetCommand,
    ProgrammeServiceNameSetCommand,
)


class TestDecodingCommands:
    def test_decoding_single_pi_msg(self):
        msgs = UECPCommand.decode_messages([0x01, 0x3F, 0xDA, 0xAB, 0xCD])
        assert len(msgs) == 1
        msg = msgs[0]
        assert isinstance(msg, ProgrammeIdentificationSetCommand)
        assert msg.pi == 0xABCD
        assert msg.programme_service_number == 0xDA
        assert msg.data_set_number == 0x3F

    def test_decode_pi_ps(self):
        msgs = UECPCommand.decode_messages(
            [
                0x01,
                0x3F,
                0xDA,
                0xAB,
                0xCD,
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
        assert len(msgs) == 2
        msg = msgs[0]
        assert isinstance(msg, ProgrammeIdentificationSetCommand)
        assert msg.pi == 0xABCD
        assert msg.programme_service_number == 0xDA
        assert msg.data_set_number == 0x3F
        msg = msgs[1]
        assert isinstance(msg, ProgrammeServiceNameSetCommand)
        assert msg.ps == "RADIO 1"
        assert msg.programme_service_number == 2
        assert msg.data_set_number == 0
