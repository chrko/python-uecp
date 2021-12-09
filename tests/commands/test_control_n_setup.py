import random

import pytest

from uecp.commands.control_n_setup import (
    CommunicationMode,
    CommunicationModeSetCommand,
    DataSetSelectCommand,
    EncoderAddressSetCommand,
    SiteAddressSetCommand,
    SiteEncoderAddressSetCommandMode,
)


class TestSiteAddressSetCommand:
    @pytest.mark.dependency
    def test_example(self):
        """\
        <23><01><00><48>
        Add the site address 00 48 hex to the list of site addresses."""
        data = [0x23, 0x01, 0x00, 0x48]
        cmd, consumed_bytes = SiteAddressSetCommand.create_from(data)
        assert consumed_bytes == 4
        assert isinstance(cmd, SiteAddressSetCommand)
        assert cmd.mode == SiteEncoderAddressSetCommandMode.ADD_SINGLE
        assert cmd.site_address == 0x48
        assert cmd.encode() == data

    @pytest.mark.dependency(depends=["TestSiteAddressSetCommand::test_example"])
    @pytest.mark.parametrize(
        "mode", list(SiteEncoderAddressSetCommandMode), ids=lambda v: f"mode-{v.name}"
    )
    @pytest.mark.parametrize(
        "site_address",
        random.sample(range(0x3FF), 5),
        ids=lambda v: f"site_address-{v}",
    )
    def test_all_possible_values(self, mode, site_address):
        cmd = SiteAddressSetCommand(mode=mode, site_address=site_address)
        data = cmd.encode()
        cmd_2, _ = SiteAddressSetCommand.create_from(data)
        assert cmd_2.encode() == data


class TestEncoderAddressSetCommand:
    @pytest.mark.dependency
    def test_example(self):
        """\
        <27><01><13>
        Add the encoder address 13 (hex) to the list of encoder ad dresses."""
        data = [0x27, 0x01, 0x13]
        cmd, consumed_bytes = EncoderAddressSetCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, EncoderAddressSetCommand)
        assert cmd.mode == SiteEncoderAddressSetCommandMode.ADD_SINGLE
        assert cmd.encoder_address == 0x13
        assert cmd.encode() == data

    @pytest.mark.dependency(depends=["TestEncoderAddressSetCommand::test_example"])
    @pytest.mark.parametrize(
        "mode", list(SiteEncoderAddressSetCommandMode), ids=lambda v: f"mode-{v.name}"
    )
    @pytest.mark.parametrize(
        "encoder_address",
        random.sample(range(0x3F), 5),
        ids=lambda v: f"encoder_address-{v}",
    )
    def test_all_possible_values(self, mode, encoder_address):
        cmd = EncoderAddressSetCommand(mode=mode, encoder_address=encoder_address)
        data = cmd.encode()
        cmd_2, _ = EncoderAddressSetCommand.create_from(data)
        assert cmd_2.encode() == data


class TestCommunicationModeSetCommand:
    def test_example(self):
        """\
        <2C><01>
        The encoder is set to bi-directional mode with requested response."""
        data = [0x2C, 0x01]
        cmd, consumed_bytes = CommunicationModeSetCommand.create_from(data)
        assert consumed_bytes == 2
        assert isinstance(cmd, CommunicationModeSetCommand)
        assert cmd.mode == CommunicationMode.BIDIRECTIONAL_REQUESTED_RESPONSE
        assert cmd.encode() == data


class TestDataSetSelectCommand:
    def test_example(self):
        """\
        <1C><17>
        Select data set >23< to be active."""
        data = [0x1C, 0x17]
        cmd, consumed_bytes = DataSetSelectCommand.create_from(data)
        assert consumed_bytes == 2
        assert isinstance(cmd, DataSetSelectCommand)
        assert cmd.data_set_number == 23
        assert cmd.encode() == data
