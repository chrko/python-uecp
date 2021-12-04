import codecs
import typing

encoding_base_table: dict[int, int] = {i: i for i in range(0x20, 0x7F)}
encoding_base_table.update(
    {
        # chars not matching ascii
        0x24: 0x00A4,
        0x5E: 0x2015,
        0x60: 0x2551,
        0x7E: 0x00AF,
        # custom character mapping
        0x80: 0x00E1,
        0x81: 0x00E0,
        0x82: 0x00E9,
        0x83: 0x00E8,
        0x84: 0x00ED,
        0x85: 0x00EC,
        0x86: 0x00F3,
        0x87: 0x00F2,
        0x88: 0x00FA,
        0x89: 0x00F9,
        0x8A: 0x00D1,
        0x8B: 0x00C7,
        0x8C: 0x015E,
        0x8D: 0x00DF,
        0x8E: 0x00A1,
        0x8F: 0x0132,
        0x90: 0x00E2,
        0x91: 0x00E4,
        0x92: 0x00EA,
        0x93: 0x00EB,
        0x94: 0x00EE,
        0x95: 0x00EF,
        0x96: 0x00F4,
        0x97: 0x00F6,
        0x98: 0x00FB,
        0x99: 0x00FC,
        0x9A: 0x00F1,
        0x9B: 0x00E7,
        0x9C: 0x015F,
        0x9D: 0x011F,
        0x9E: 0x0131,
        0x9F: 0x0133,
        0xA0: 0x00AA,
        0xA1: 0x03B1,
        0xA2: 0x00A9,
        0xA3: 0x2030,
        0xA4: 0x011E,
        0xA5: 0x011B,
        0xA6: 0x0148,
        0xA7: 0x0151,
        0xA8: 0x03C0,
        0xA9: 0x20AC,
        0xAA: 0x00A3,
        0xAB: 0x0024,
        0xAC: 0x2190,
        0xAD: 0x2191,
        0xAE: 0x2192,
        0xAF: 0x2193,
        0xB0: 0x00BA,
        0xB1: 0x00B9,
        0xB2: 0x00B2,
        0xB3: 0x00B3,
        0xB4: 0x00B1,
        0xB5: 0x0130,
        0xB6: 0x0144,
        0xB7: 0x0171,
        0xB8: 0x00B5,
        0xB9: 0x00BF,
        0xBA: 0x00F7,
        0xBB: 0x00B0,
        0xBC: 0x00BC,
        0xBD: 0x00BD,
        0xBE: 0x00BE,
        0xBF: 0x00A7,
        0xC0: 0x00C1,
        0xC1: 0x00C0,
        0xC2: 0x00C9,
        0xC3: 0x00C8,
        0xC4: 0x00CD,
        0xC5: 0x00CC,
        0xC6: 0x00D3,
        0xC7: 0x00D2,
        0xC8: 0x00DA,
        0xC9: 0x00D9,
        0xCA: 0x0158,
        0xCB: 0x010C,
        0xCC: 0x0160,
        0xCD: 0x017D,
        0xCE: 0x00D0,
        0xCF: 0x013F,
        0xD0: 0x00C2,
        0xD1: 0x00C4,
        0xD2: 0x00CA,
        0xD3: 0x00CB,
        0xD4: 0x00CE,
        0xD5: 0x00CF,
        0xD6: 0x00D4,
        0xD7: 0x00D6,
        0xD8: 0x00DB,
        0xD9: 0x00DC,
        0xDA: 0x0159,
        0xDB: 0x010D,
        0xDC: 0x0161,
        0xDD: 0x017E,
        0xDF: 0x0140,
        0xE0: 0x00C3,
        0xE1: 0x00C5,
        0xE2: 0x00C6,
        0xE3: 0x0152,
        0xE4: 0x0177,
        0xE5: 0x00DD,
        0xE6: 0x00D5,
        0xE7: 0x00D8,
        0xE8: 0x00DE,
        0xE9: 0x014A,
        0xEA: 0x0154,
        0xEB: 0x0106,
        0xEC: 0x015A,
        0xED: 0x0179,
        0xEE: 0x0166,
        0xEF: 0x00F0,
        0xF0: 0x00E3,
        0xF1: 0x00E5,
        0xF2: 0x00E6,
        0xF3: 0x0153,
        0xF4: 0x0175,
        0xF5: 0x00FD,
        0xF6: 0x00F5,
        0xF7: 0x00F8,
        0xF8: 0x00FE,
        0xF9: 0x014B,
        0xFA: 0x0155,
        0xFB: 0x0107,
        0xFC: 0x015B,
        0xFD: 0x017A,
        0xFE: 0x0167,
    }
)

encoding_table = {}
decoding_table = {}

for (character_code, unicode_number) in encoding_base_table.items():
    unicode_char = chr(unicode_number)

    if unicode_char in encoding_table:
        raise Exception(
            f"unicode_char {unicode_char} already mapped to {encoding_table[unicode_char]:#x}"
        )
    encoding_table[unicode_char] = character_code

    if character_code in decoding_table:
        raise Exception()
    decoding_table[character_code] = unicode_char


def encode(input_string: str, errors: str = "strict") -> tuple[bytes, int]:
    encoded = []
    encoded_chars = 0

    for char in input_string:
        try:
            encoded.append(encoding_table[char])
            encoded_chars += 1
        except KeyError:
            if errors == "strict":
                raise UnicodeError(f"Cannot encode {char}, code point {ord(char):#x}")
    return bytes(encoded), encoded_chars


def decode(data: bytes, errors: str = "strict") -> tuple[str, int]:
    decoded = ""
    decoded_chars = 0

    for byte in list(data):
        try:
            decoded += decoding_table[byte]
            decoded_chars += 1
        except KeyError:
            if errors == "strict":
                raise UnicodeError(f"Cannot decode byte {byte:#x}")

    return decoded, decoded_chars


class Codec(codecs.Codec):
    def encode(self, input_string: str, errors: str = "strict") -> tuple[bytes, int]:
        return encode(input_string, errors)

    def decode(self, data: bytes, errors: str = "strict") -> tuple[str, int]:
        return decode(data, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, data: str, final: bool = False) -> bytes:
        return encode(data, errors=self.errors)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, data: bytes, final: bool = False) -> str:
        return decode(data, errors=self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    """encodings module API"""
    return codecs.CodecInfo(
        name="basic_rds_character_set",
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
        _is_text_encoding=True,
    )


def search_function(name: str) -> typing.Optional[codecs.CodecInfo]:
    if name in ["basic_rds_character_set", "rds_character_set", "rds"]:
        return getregentry()
    return None


codecs.register(search_function)
