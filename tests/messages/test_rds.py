import pytest

from uecp.messages import ProgrammeIdentificationMessage


class TestPIMessage:
    def test_encoding(self):
        msg = ProgrammeIdentificationMessage(
            pi=0xABCD, data_set_number=0x3F, programme_service_number=0xDA
        )
        assert msg.encode() == [0x01, 0x3F, 0xDA, 0xAB, 0xCD]

    def test_create_from(self):
        msg, consumed_bytes = ProgrammeIdentificationMessage.create_from(
            [0x01, 0x3F, 0xDA, 0xAB, 0xCD]
        )
        assert msg.pi == 0xABCD
        assert msg.programme_service_number == 0xDA
        assert msg.data_set_number == 0x3F
        assert consumed_bytes == 5

        with pytest.raises(ValueError):
            ProgrammeIdentificationMessage.create_from([0x01])

        with pytest.raises(ValueError):
            ProgrammeIdentificationMessage.create_from([0xF1, 0x02, 0x03, 0x04, 0x05])
