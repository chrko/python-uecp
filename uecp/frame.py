import codecs

from crc import Configuration, CrcCalculator

from uecp.commands import UECPCommand


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

    def __init__(self):
        self._site_address: int = 0
        self._encoder_address: int = 0
        self._sequence_counter: int = 0
        self._commands: list[UECPCommand] = []

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

    def add_command(self, msg):
        self._commands.append(msg)

    def clear_commands(self):
        self._commands = []

    def encode(self) -> list[int]:
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

        data = list(codecs.encode(data, "uecp_frame"))

        return [self.STA] + data + [self.STP]
