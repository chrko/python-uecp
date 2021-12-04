import random

import pytest
from crc import CrcCalculator

from uecp import __version__
from uecp.frame import UECPFrame
from uecp.commands import ProgrammeIdentificationSetCommand


def test_version():
    assert __version__ == "0.0.1"


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

        f.add_message(ProgrammeIdentificationSetCommand(pi=0xFF))
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
