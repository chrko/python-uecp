from uecp.commands.base import UECPCommand
from uecp.commands.rds_message import (
    ProgrammeIdentificationSetCommand,
    ProgrammeServiceNameSetCommand,
)


def test_command_count():
    assert len(UECPCommand.ELEMENT_CODE_MAP) == 19


class TestDecodingCommands:
    def test_decoding_single_pi_cmd(self):
        cmds = UECPCommand.decode_commands([0x01, 0x3F, 0xDA, 0xAB, 0xCD])
        assert len(cmds) == 1
        cmd = cmds[0]
        assert isinstance(cmd, ProgrammeIdentificationSetCommand)
        assert cmd.pi == 0xABCD
        assert cmd.programme_service_number == 0xDA
        assert cmd.data_set_number == 0x3F

    def test_decode_pi_ps(self):
        cmds = UECPCommand.decode_commands(
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
        assert len(cmds) == 2
        cmd = cmds[0]
        assert isinstance(cmd, ProgrammeIdentificationSetCommand)
        assert cmd.pi == 0xABCD
        assert cmd.programme_service_number == 0xDA
        assert cmd.data_set_number == 0x3F
        cmd = cmds[1]
        assert isinstance(cmd, ProgrammeServiceNameSetCommand)
        assert cmd.ps == "RADIO 1"
        assert cmd.programme_service_number == 2
        assert cmd.data_set_number == 0
