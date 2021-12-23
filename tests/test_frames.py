import random

import pytest
from crc import CrcCalculator

from uecp.commands import (
    DataSetSelectCommand,
    MessageAcknowledgementCommand,
    ProgrammeIdentificationSetCommand,
)
from uecp.commands.bidirectional import ResponseCode
from uecp.frame import UECPFrame, UECPFrameDecoder


class TestUECPFrame:
    def test_site_address(self):
        f = UECPFrame()
        assert f.encoder_address == 0

        with pytest.raises(ValueError, match="0xfff given"):
            f.site_address = 0xFFF
        assert f.site_address == 0

        with pytest.raises(ValueError, match="-0x5 given"):
            f.site_address = -5
        assert f.site_address == 0

        with pytest.raises(ValueError, match="Site address must be an integer"):
            f.site_address = 5.5
        assert f.site_address == 0

        f.site_address = 0x35
        assert f.site_address == 0x35

    def test_encoder_address(self):
        f = UECPFrame()
        assert f.encoder_address == 0

        with pytest.raises(ValueError, match="0xff given"):
            f.encoder_address = 0xFF
        assert f.encoder_address == 0

        with pytest.raises(ValueError, match="-0x5 given"):
            f.encoder_address = -5
        assert f.encoder_address == 0

        with pytest.raises(ValueError, match="Encoder address must be an integer"):
            f.encoder_address = 5.5
        assert f.encoder_address == 0

        f.encoder_address = 0x33
        assert f.encoder_address == 0x33

    def test_sequence_counter(self):
        f = UECPFrame()
        assert f.sequence_counter == 0

        with pytest.raises(ValueError, match="0xeff given"):
            f.sequence_counter = 0xEFF
        assert f.sequence_counter == 0

        with pytest.raises(ValueError, match="-0x5 given"):
            f.sequence_counter = -5
        assert f.sequence_counter == 0

        with pytest.raises(ValueError, match="Sequence counter must be an integer"):
            f.sequence_counter = 5.5
        assert f.sequence_counter == 0

        f.sequence_counter = 0x33
        assert f.sequence_counter == 0x33

    def test_encode(self):
        f = UECPFrame()
        res = f.encode()
        assert bytes(res).hex() == "fe000000007b3fff"

        f.sequence_counter = 0xFE
        res = f.encode()
        assert bytes(res).hex() == "fe0000fd01004bf1ff"

        f.add_command(ProgrammeIdentificationSetCommand(pi=0xFF))
        res = f.encode()
        assert bytes(res).hex() == "fe0000fd010501000000fd020d3dff"


def test_crc():
    def crc_ccitt(data):
        """\
        This implementation is copied from https://github.com/mpbraendli/mmbtools-aux/blob/master/uecpparse/crc.py
        to verify configuration of crc library
        """
        crc = 0xFFFF

        for d in data:
            crc = (((crc >> 8) & 0xFF) | (crc << 8)) & 0xFFFF
            crc ^= d
            crc ^= ((crc & 0xFF) >> 4) & 0xFFFF
            crc ^= ((crc << 8) << 4) & 0xFFFF
            crc ^= (((crc & 0xFF) << 4) << 1) & 0xFFFF

        return (crc ^ 0xFFFF) & 0xFFFF

    d = random.randbytes(10)
    crc_calculator = CrcCalculator(UECPFrame.CRC_CONFIGURATION)
    crc = crc_calculator.calculate_checksum(d)
    crc2 = crc_ccitt(d)
    assert crc == crc2
    assert crc_calculator.verify_checksum(d, crc2)


class TestUECPFrameDecoder:
    def test_acknowledge(self):
        data = [0xFE, 0x00, 0x00, 0x2A, 0x02, 0x18, 0x00, 0x4A, 0xB0, 0xFF]

        decoder = UECPFrameDecoder()
        frame, decoded_bytes = decoder.decode(data[:3])
        assert frame is None
        assert decoded_bytes == 3
        frame, decoded_bytes = decoder.decode(data[3:])
        assert frame is not None
        assert decoded_bytes == 7

        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0x2A
        commands = frame.commands
        assert len(commands) == 1
        command = commands[0]
        assert isinstance(command, MessageAcknowledgementCommand)
        assert command.code is ResponseCode.OK

    def test_data_set_response(self):
        data = bytes.fromhex("FE00002B021C02D082FF")
        decoder = UECPFrameDecoder()
        frame, decoded_bytes = decoder.decode(data)
        assert frame is not None
        assert decoded_bytes == 10
        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0x2B
        commands = frame.commands
        assert len(commands) == 1
        command = commands[0]
        assert isinstance(command, DataSetSelectCommand)
        assert command.select_data_set_number == 2

    def test_data_set_response_complete(self):
        decoder = UECPFrameDecoder()

        data = bytes.fromhex("fe 00 00 c5 02 18 00 1a b4 ff")

        frame, decoded_bytes = decoder.decode(data[:3])
        assert frame is None
        assert decoded_bytes == 3
        frame, decoded_bytes = decoder.decode(data[3:])
        assert frame is not None
        assert decoded_bytes == 7

        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0xC5
        commands = frame.commands
        assert len(commands) == 1
        command = commands[0]
        assert isinstance(command, MessageAcknowledgementCommand)
        assert command.code is ResponseCode.OK

        data = bytes.fromhex("fe 00 00 c6 02 1c 02 6d ee ff")
        frame, decoded_bytes = decoder.decode(data)
        assert frame is not None
        assert decoded_bytes == 10
        assert frame.site_address == 0
        assert frame.encoder_address == 0
        assert frame.sequence_counter == 0xC6
        commands = frame.commands
        assert len(commands) == 1
        command = commands[0]
        assert isinstance(command, DataSetSelectCommand)
        assert command.select_data_set_number == 2
