import pytest

from uecp import rds_character_set_codec


def test_encoding_table():
    assert rds_character_set_codec.encoding_table["ä"] == 0x91
    assert rds_character_set_codec.encoding_table["@"] == 0x40
    assert "\t" not in rds_character_set_codec.encoding_table


def test_decoding_table():
    assert 0x7F not in rds_character_set_codec.decoding_table
    assert 0xFF not in rds_character_set_codec.decoding_table


def test_encoding():
    assert "My Progräm#".encode("rds") == b"My Progr\x91m#"
    assert "¹²³".encode("rds") == b"\xB1\xB2\xB3"

    with pytest.raises(UnicodeError):
        "\0".encode("rds")


def test_decoding():
    assert b"\xD7".decode("rds") == "Ö"
    with pytest.raises(UnicodeError):
        b"\0".decode("rds")


@pytest.mark.parametrize("data", ["radio", "sthörfunk"])
def test_round_trip(data: str):
    assert data.encode("rds").decode("rds") == data
