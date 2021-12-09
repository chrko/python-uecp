from uecp.commands.bidirectional import (
    MessageAcknowledgementCommand,
    RequestCommand,
    ResponseCode,
)


class TestMessageAcknowledgementCommand:
    def test_example_1(self):
        """\
        <18><00>
        In the bidirectional mode 1: All messages after the last response were correctly
        received. In the bidirectional mode 2: the last message was correctly received.
        """
        data = [0x18, 0x00]
        cmd, consumed_bytes = MessageAcknowledgementCommand.create_from(data)
        assert consumed_bytes == 2
        assert isinstance(cmd, MessageAcknowledgementCommand)
        assert cmd.code is ResponseCode.OK
        assert cmd.sequence_counter == 0
        assert cmd.encode() == data

    def test_example_2(self):
        """\
        <18> <02> <42> means that sequence number 42 hex is wrong."""
        data = [0x18, 0x02, 0x42]
        cmd, consumed_bytes = MessageAcknowledgementCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, MessageAcknowledgementCommand)
        assert cmd.code is ResponseCode.MSG_NOT_RECEIVED
        assert cmd.sequence_counter == 0x42
        assert cmd.encode() == data


class TestRequestCommand:
    def test_example(self):
        data = [0x17, 0x03, 0x01, 0x44, 0x32]
        cmd, consumed_bytes = RequestCommand.create_from(data)
        assert consumed_bytes == 5
        assert isinstance(cmd, RequestCommand)
        assert cmd.element_code == 0x01
        assert cmd.data_set_number == 0x44
        assert cmd.programme_service_number == 0x32
        assert cmd._additional_data == []
        assert cmd.encode() == data
