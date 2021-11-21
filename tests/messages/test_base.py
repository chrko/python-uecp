from uecp.messages.base import UECPMessage
from uecp.messages.rds import ProgrammeIdentificationMessage


class TestDecodingMessages:
    def test_decoding_single_pi_msg(self):
        msgs = UECPMessage.decode_messages([0x01, 0x3F, 0xDA, 0xAB, 0xCD])
        assert len(msgs) == 1
        msg = msgs[0]
        assert isinstance(msg, ProgrammeIdentificationMessage)
        assert msg.pi == 0xABCD
        assert msg.programme_service_number == 0xDA
        assert msg.data_set_number == 0x3F
