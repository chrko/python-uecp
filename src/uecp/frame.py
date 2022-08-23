import codecs
import typing

from crc import Configuration, CrcCalculator  # type: ignore

from uecp.byte_stuffing_codec import (
    IncrementalDecoder as ByteStuffingIncrementalDecoder,
)
from uecp.commands.base import UECPCommand


class UECPFrame:
    STA = 0xFE
    STP = 0xFF

    ALL_SITES = 0
    ALL_ENCODERS = 0

    UNUSED_SEQUENCE_COUNTER = 0

    CRC_CONFIGURATION = Configuration(
        width=16,
        polynomial=0x1021,
        init_value=0xFFFF,
        final_xor_value=0xFFFF,
        reverse_input=False,
        reverse_output=False,
    )

    def __init__(
        self,
        site_address=0,
        encoder_address=0,
        sequence_counter=0,
        commands: typing.Optional[list[UECPCommand]] = None,
    ):
        self._site_address: int = 0
        self._encoder_address: int = 0
        self._sequence_counter: int = 0
        self._commands: list[UECPCommand] = []

        self.site_address = site_address
        self.encoder_address = encoder_address
        self.sequence_counter = sequence_counter

        self._assumed_command_length = 0
        if commands is not None:
            for command in commands:
                self.add_command(command)

    @property
    def site_address(self) -> int:
        return self._site_address

    @site_address.setter
    def site_address(self, new_site_address: int):
        if not (0 <= new_site_address <= 0x3FF):
            raise ValueError(
                f"Site address must be in range of 0 to 0x3ff, {new_site_address:#x} given"
            )
        if new_site_address != int(new_site_address):
            raise ValueError("Site address must be an integer")
        self._site_address = int(new_site_address)

    @property
    def encoder_address(self) -> int:
        return self._encoder_address

    @encoder_address.setter
    def encoder_address(self, new_encoder_address: int):
        if not (0 <= new_encoder_address <= 0x3F):
            raise ValueError(
                f"Encoder address must be in range of 0 to 0x3f, {new_encoder_address:#x} given"
            )
        if new_encoder_address != int(new_encoder_address):
            raise ValueError("Encoder address must be an integer")
        self._encoder_address = int(new_encoder_address)

    @property
    def sequence_counter(self) -> int:
        return self._sequence_counter

    @sequence_counter.setter
    def sequence_counter(self, new_sequence_counter: int):
        if not (0 <= new_sequence_counter <= 0xFF):
            raise ValueError(
                f"Sequence counter must be in range of 0 to 0xff, {new_sequence_counter:#x} given"
            )
        if new_sequence_counter != int(new_sequence_counter):
            raise ValueError("Sequence counter must be an integer")
        self._sequence_counter = int(new_sequence_counter)

    def add_command(self, *commands: UECPCommand):
        for command in commands:
            cmd_len = len(command.encode())
            if self._assumed_command_length + cmd_len > 255:
                raise OverflowError()
            self._assumed_command_length += cmd_len
            self._commands.append(command)

    def clear_commands(self):
        self._commands = []

    @property
    def commands(self) -> list[UECPCommand]:
        return list(self._commands)

    def encode(self) -> bytes:
        data: list[int] = []

        # address composed by 10 bits sites address & 6 bits encoder address
        address = self._site_address << 6 | self._encoder_address

        data.append(address >> 8)
        data.append(address & 0xFF)
        data.append(self._sequence_counter)

        msg_data: list[int] = []
        for command in self._commands:
            msg_data += command.encode()

        if not (0 <= len(msg_data) <= 255):
            raise ValueError("Encoded commands must not exceed 255 bytes")

        data.append(len(msg_data))
        data += msg_data

        crc_calculator = CrcCalculator(self.CRC_CONFIGURATION)
        crc = crc_calculator.calculate_checksum(data)
        data.append(crc >> 8)
        data.append(crc & 0xFF)

        data = list(codecs.encode(data, "uecp_frame"))  # type: ignore

        return bytes([self.STA] + data + [self.STP])

    @classmethod
    def create_from_enclosed(cls, data: typing.Union[bytes, list[int]]) -> "UECPFrame":
        if len(data) < 6:
            raise ValueError("not enough data")

        data, crc_high, crc_low = data[:-2], data[-2], data[-1]
        crc = crc_high << 8 | crc_low

        crc_calculator = CrcCalculator(cls.CRC_CONFIGURATION)
        crc_computed = crc_calculator.calculate_checksum(data)
        if crc != crc_computed:
            raise ValueError(f"CRC error {crc} vs {crc_computed}")

        address_high, address_low, sequence_counter = data[0:3]
        msg_len, msg_data = data[3], data[4:]
        if msg_len != len(msg_data):
            raise ValueError(
                f"Data length doesn't match, expected {msg_len}, given {len(msg_data)}"
            )

        address = address_high << 8 | address_low

        site_address = address >> 6
        encoder_address = address & 0x3F

        commands = UECPCommand.decode_commands(msg_data)

        return cls(
            site_address=site_address,
            encoder_address=encoder_address,
            sequence_counter=sequence_counter,
            commands=commands,
        )


class UECPFrameDecoder:
    def __init__(self):
        self._start_bit_seen = False
        self._enclosed_data = []
        self._enclosed_incremental_decoder = ByteStuffingIncrementalDecoder()

    def decode(
        self, data: typing.Union[bytes, list[int]]
    ) -> tuple[typing.Optional[UECPFrame], typing.Union[bytes, list[int]]]:
        i = 0

        try:
            for i, byte in enumerate(data, start=1):
                if byte == UECPFrame.STA:
                    self._start_bit_seen = True
                elif byte == UECPFrame.STP:
                    if self._start_bit_seen is False:
                        raise ValueError("Stop bit seen, but no start bit")
                    if len(self._enclosed_data) <= 1:
                        raise ValueError("No payload data decoded")
                    frame = UECPFrame.create_from_enclosed(self._enclosed_data)
                    self.reset()
                    return frame, data[i:]
                else:
                    self._enclosed_data += list(
                        self._enclosed_incremental_decoder.decode([byte])
                    )
        except Exception as e:
            self.reset()
            raise e

        return None, data[i:]

    def reset(self):
        self._enclosed_data.clear()
        self._enclosed_incremental_decoder.reset()
        self._start_bit_seen = False

    @property
    def empty(self) -> bool:
        return (
            len(self._enclosed_data) == 0
            and self._enclosed_incremental_decoder.getstate()[1] == 1
        )
