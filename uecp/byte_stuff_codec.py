import codecs
import typing
from typing import Tuple


def byte_stuffing(
    data: typing.Union[list[int], bytes], errors: str = "strict"
) -> list[int]:
    stuffed_data = []
    for byte in list(data):
        if byte == 0xFD:
            stuffed_data += [0xFD, 0x00]
        elif byte == 0xFE:
            stuffed_data += [0xFD, 0x01]
        elif byte == 0xFF:
            stuffed_data += [0xFD, 0x02]
        else:
            stuffed_data += [byte]

    return stuffed_data


def byte_stuffing_reverse(
    stuffed_data: typing.Union[list[int], bytes], errors: str = "strict"
) -> list[int]:
    data = []
    next_byte_stuffed = False
    for byte in list(stuffed_data):
        if 0x00 <= byte < 0xFD and not next_byte_stuffed:
            data.append(byte)
        elif byte == 0xFD and not next_byte_stuffed:
            next_byte_stuffed = True
        elif 0x00 <= byte <= 0x02 and next_byte_stuffed:
            data.append(byte + 0xFD)
            next_byte_stuffed = False
        else:
            if errors == "strict":
                raise UnicodeError(
                    f"Unknown state, byte {byte:#x}, next_byte_stuffed {next_byte_stuffed}"
                )

    return data


class Codec(codecs.Codec):
    def encode(self, data: bytes, errors: str = "strict") -> Tuple[bytes, int]:
        return bytes(byte_stuffing(data)), len(data)

    def decode(self, data: bytes, errors: str = "strict") -> Tuple[bytes, int]:
        return bytes(byte_stuffing_reverse(data), errors=errors), len(data)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, data: bytes, final: bool = False) -> bytes:
        return bytes(byte_stuffing(data))


class IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors: str = "strict"):
        self.errors = errors
        self.next_byte_stuffed = False

    def reset(self):
        self.next_byte_stuffed = True

    def getstate(self) -> Tuple[bytes, int]:
        return bytes(), int(self.next_byte_stuffed)

    def setstate(self, state: Tuple[bytes, int]):
        self.next_byte_stuffed = bool(state[1])

    def decode(self, data: bytes, final: bool = False) -> bytes:
        decoded = []
        for byte in list(data):
            if 0x00 <= byte < 0xFD and not self.next_byte_stuffed:
                decoded.append(byte)
            elif byte == 0xFD and not self.next_byte_stuffed:
                self.next_byte_stuffed = True
            elif 0x00 <= byte <= 0x02 and self.next_byte_stuffed:
                decoded.append(byte + 0xFD)
                self.next_byte_stuffed = False
            else:
                if self.errors == "strict":
                    raise UnicodeError(
                        f"Unknown state, byte {byte:#x}, next_byte_stuffed {self.next_byte_stuffed}"
                    )

        if final:
            self.next_byte_stuffed = False

        return bytes(decoded)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    """encodings module API"""
    return codecs.CodecInfo(
        name="uecp-frame",
        encode=byte_stuffing,
        decode=byte_stuffing_reverse,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


def search_function(name: str) -> typing.Optional[codecs.CodecInfo]:
    if name in ["uecp-frame"]:
        return getregentry()
    return None


codecs.register(search_function)
