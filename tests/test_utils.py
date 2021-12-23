import textwrap
import typing

import pytest


def from_arcos(data: str) -> bytes:
    data = data.rsplit("-")[-1]
    data = data.rsplit(">")[-1]
    data = data.replace(",", "")
    return bytes.fromhex(data)


def to_arcos(data: typing.Union[bytes, list[int]]) -> str:
    data = bytes(data).hex()
    data = textwrap.wrap(data, 2)
    data = ",".join(data).upper()
    return data


@pytest.mark.parametrize(
    "test_input",
    [
        "FE,00,00,00,07,2D,05,52,53,D8,01,01,7B,66,FF",
        "23/12/2021 13:51:25.771 - FE,00,00,00,07,2D,05,52,53,D8,01,01,7B,66,FF",
    ],
)
def test_from_arcos(test_input):
    output_data = bytes.fromhex("FE 00 00 00 07 2D 05 52 53 D8 01 01 7B 66 FF")
    assert from_arcos(test_input) == output_data


def test_from_arcos_2():
    input_data = """--> FE,00,00,01,1A,0A,01,00,04,0A,52,44,53,0A,01,00,0E,46,D9,62,65,6C,73,74,20,67,65,69,6C,20,32,68,0C,FF"""
    assert from_arcos(input_data) == bytes.fromhex(
        "FE0000011A0A0100040A5244530A01000E46D962656C7374206765696C2032680CFF"
    )
    input_data = """<-- FE,00,00,32,02,18,00,D4,D4,FF"""
    assert from_arcos(input_data) == bytes.fromhex("FE000032021800D4D4FF")


@pytest.mark.parametrize(
    "test_input",
    [[0x43, 0xCD, 0x53, 0xFF, 0xE2, 0xDD], b"\x43\xcd\x53\xff\xe2\xdd"],
)
def test_to_arcos(test_input):
    assert to_arcos(test_input) == "43,CD,53,FF,E2,DD"
