from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from uecp.commands.clock_control import (
    RealTimeClockCorrectionSetCommand,
    RealTimeClockEnabledSetCommand,
    RealTimeClockSetCommand,
)


class TestRealTimeClockSetCommand:
    def test_create_from(self):
        """\
        <0D><02><09><0C><0A><12><21><0F><02>
        The following is to be set: Year is 2002, Month is September, Date is 12, Hour is 10,
        Minute is 18, Second is 33, Centisecond is 15 and Local Time offset is 1 hour."""

        data = [0x0D, 0x02, 0x09, 0x0C, 0x0A, 0x12, 0x21, 0x0F, 0x02]
        cmd, consumed_bytes = RealTimeClockSetCommand.create_from(data)
        assert consumed_bytes == 9
        assert isinstance(cmd, RealTimeClockSetCommand)
        assert cmd.timestamp == datetime(
            year=2002,
            month=9,
            day=12,
            hour=11,
            minute=18,
            second=33,
            microsecond=150_000,
            tzinfo=timezone(timedelta(seconds=3600)),
        )
        assert cmd.encode() == data

    def test_encode(self):
        ts = datetime(
            year=2002,
            month=9,
            day=12,
            hour=11,
            minute=18,
            second=33,
            microsecond=150_000,
            tzinfo=ZoneInfo("Europe/London"),
        )
        cmd = RealTimeClockSetCommand(timestamp=ts)
        assert cmd.encode() == [0x0D, 0x02, 0x09, 0x0C, 0x0A, 0x12, 0x21, 0x0F, 0x02]


class TestRealTimeClockCorrectionSetCommand:
    def test_create_from(self):
        data = [0x09, 0xFF, 0xC6]
        cmd, consumed_bytes = RealTimeClockCorrectionSetCommand.create_from(data)
        assert consumed_bytes == 3
        assert isinstance(cmd, RealTimeClockCorrectionSetCommand)
        assert cmd.adjustment_ms == -58
        assert cmd.encode() == data

    def test_encode(self):
        cmd = RealTimeClockCorrectionSetCommand(adjustment_ms=-169)
        assert cmd.encode() == [0x09, 0xFF, 0x57]


class TestRealTimeClockEnabledSetCommand:
    def test_create_from(self):
        data = [0x19, 0x01]
        cmd, consumed_bytes = RealTimeClockEnabledSetCommand.create_from(data)
        assert consumed_bytes == 2
        assert isinstance(cmd, RealTimeClockEnabledSetCommand)
        assert cmd.enable is True
        assert cmd.encode() == data
