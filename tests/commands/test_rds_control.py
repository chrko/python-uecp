import random

import pytest

from uecp.commands import RDSEnabledSetCommand, RDSPhaseSetCommand
from uecp.commands.rds_control import RDSLevelSetCommand


class TestRDSEnabledSetCommand:
    def test_create_from(self):
        """\
        <1E><00>
        Switch the RDS output signal "Off".
        """
        data = [0x1E, 0x00]
        cmd, consumed_bytes = RDSEnabledSetCommand.create_from(data)
        assert consumed_bytes == 2
        assert isinstance(cmd, RDSEnabledSetCommand)
        assert cmd.enable is False
        assert cmd.encode() == data


class TestRDSPhaseSetCommand:
    def test_create_from_2(self):
        data = [0x22, 0x85, 0x46]
        cmd, consumed_bytes = RDSPhaseSetCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, RDSPhaseSetCommand)
        assert cmd.reference_table == 4
        assert cmd.deci_degrees == 1350
        assert cmd.encode() == data

    @pytest.mark.dependency()
    def test_encode(self):
        cmd = RDSPhaseSetCommand(reference_table=4, deci_degrees=1356)
        assert cmd.encode() == [0x22, 0x85, 0x4C]

    @pytest.mark.dependency(depends=["TestRDSPhaseSetCommand::test_encode"])
    def test_create_from(self):
        """\
        <22><45><4C>
        Set phase to 135.6 degrees for Reference Table entry: Input 4.
        """
        data = [0x22, 0x85, 0x4C]
        cmd, consumed_bytes = RDSPhaseSetCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, RDSPhaseSetCommand)
        assert cmd.reference_table == 4
        assert cmd.deci_degrees == 1356
        assert cmd.encode() == data

    @pytest.mark.dependency(depends=["TestRDSPhaseSetCommand::test_create_from"])
    @pytest.mark.parametrize(
        "deci_degrees",
        random.sample(range(3600), 5),
        ids=lambda v: f"deci_degrees-{v}",
    )
    @pytest.mark.parametrize(
        "reference_table", list(range(8)), ids=lambda v: f"ref_table-{v}"
    )
    def test_all_possible_values(self, reference_table, deci_degrees):
        cmd = RDSPhaseSetCommand(
            reference_table=reference_table, deci_degrees=deci_degrees
        )
        data = cmd.encode()
        cmd_2, _ = RDSPhaseSetCommand.create_from(data)
        assert cmd.reference_table == cmd_2.reference_table
        assert cmd.deci_degrees == cmd_2.deci_degrees
        assert cmd_2.encode() == data


class TestRDSLevelSetCommand:
    @pytest.mark.dependency()
    def test_create_from(self):
        """\
        <0E><A3><11>
        Set RDS level to 785 mV_{p-p} for Reference Table entry: input 5.
        """
        data = [0x0E, 0xA3, 0x11]
        cmd, consumed_bytes = RDSLevelSetCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, RDSLevelSetCommand)
        assert cmd.reference_table == 5
        assert cmd.level == 785
        assert cmd.encode() == data

    @pytest.mark.dependency(depends=["TestRDSLevelSetCommand::test_create_from"])
    @pytest.mark.parametrize(
        "level", random.sample(range(8192), 5), ids=lambda v: f"level-{v}"
    )
    @pytest.mark.parametrize(
        "reference_table", list(range(8)), ids=lambda v: f"ref_table-{v}"
    )
    def test_all_possible_values(self, reference_table, level):
        cmd = RDSLevelSetCommand(reference_table=reference_table, level=level)
        data = cmd.encode()
        cmd_2, _ = RDSLevelSetCommand.create_from(data)
        assert cmd_2.encode() == data
