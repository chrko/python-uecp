import codecs

import pytest

from uecp.byte_stuffing_codec import encode, decode


class TestByteStuffingFunctions:
    def test_simple_input(self):
        data = [0xFF, 0xFD, 0x01, 0x54, 0x44]
        res = encode(data)

        assert list(res[0]) == [0xFD, 0x02, 0xFD, 0x00, 0x01, 0x54, 0x44]
        assert res[1] == 5

    def test_round_trip(self):
        data = [0xFF, 0xFD, 0x01, 0x54, 0xFD, 0x44]
        assert list(decode(encode(data)[0])[0]) == data

    @pytest.mark.parametrize(
        "stuffed_data",
        [[0xFF, 0x00, 0x01], [0xFD, 0xFD], [0xFD, 0x03], [0xFE, 0x04], [0xEF, 0xFD]],
    )
    def test_invalid_input(self, stuffed_data):
        with pytest.raises(UnicodeError):
            decode(stuffed_data)


class TestRegisteredCodec:
    codec_info = codecs.lookup("uecp-frame")

    def test_encoder(self):
        res = self.codec_info.encode(bytes([0xFF, 0xFD, 0x01, 0x54, 0x44]))

        assert list(res[0]) == [0xFD, 0x02, 0xFD, 0x00, 0x01, 0x54, 0x44]
        assert res[1] == 5

    def test_decoder(self):
        res = self.codec_info.decode(bytes([0xFD, 0x02, 0xFD, 0x00, 0x01, 0x54, 0x44]))

        assert list(res[0]) == [0xFF, 0xFD, 0x01, 0x54, 0x44]
        assert res[1] == 7

    def test_incremental_decoder(self):
        decoder = self.codec_info.incrementaldecoder()
        assert decoder.decode(b"\xFD") == b""
        assert decoder.decode(b"\x01") == b"\xFE"

        with pytest.raises(UnicodeError):
            decoder.decode(b"\xFD", True)

        decoder.reset()

        assert decoder.decode(b"\xFD") == b""
        with pytest.raises(UnicodeError):
            decoder.decode(b"\xFF")

        decoder.reset()
        decoder.errors = "ignore"

        assert decoder.decode(b"\xFD", True) == b""

        decoder.reset()
        assert decoder.decode(b"\xFD\x01\x02") == b"\xFE\x02"
