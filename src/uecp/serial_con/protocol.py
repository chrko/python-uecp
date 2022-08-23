import asyncio
import logging
import typing
from asyncio import transports
from typing import Optional

import serial  # type: ignore
import serial_asyncio  # type: ignore

from uecp.frame import UECPFrame, UECPFrameDecoder


class UECPSerialProtocol(asyncio.Protocol):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__qualname__)
        self._transport: Optional[serial_asyncio.SerialTransport] = None

        self._uecp_frame_decoder = UECPFrameDecoder()

        self.connection_made_callbacks: list[typing.Callable[[], None]] = []
        self.received_frame_callbacks: list[typing.Callable[[UECPFrame], None]] = []

    @property
    def connected(self) -> bool:
        if self._transport:
            return not self._transport.is_closing()
        return False

    def connection_made(self, transport: transports.BaseTransport):
        self.logger.debug(f"Connection made {transport}")
        if self._transport is not None:
            raise ValueError("Connection already open?")
        self._transport = transport
        for callback in self.connection_made_callbacks:
            callback()

    def connection_lost(self, exc: Optional[Exception]):
        self._transport = None
        if exc is None:
            if not self._uecp_frame_decoder.empty:
                raise Exception("Interrupted within decoding a frame")
            return
        raise exc

    def data_received(self, data: bytes):
        self.logger.debug(f"Data received {data.hex()}")

        frame, remaining_data = self._uecp_frame_decoder.decode(data)
        while frame is not None:
            if frame:
                for callback in self.received_frame_callbacks:
                    callback(frame)
            frame, remaining_data = self._uecp_frame_decoder.decode(remaining_data)
        if len(remaining_data) > 0:
            raise Exception(
                f"not all received bytes could be decoded, should never happen, {remaining_data!r}"
            )

    def write(self, frame: UECPFrame):
        if self._transport:
            data = frame.encode()
            self.logger.debug(f"Writing {data.hex()}")
            self._transport.write(data)
        else:
            self.logger.error("No transport opened yet")


async def open_serial_protocol(port: str, baudrate: int) -> UECPSerialProtocol:
    con = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    )

    _, protocol = await serial_asyncio.connection_for_serial(
        asyncio.get_running_loop(), UECPSerialProtocol, con
    )
    return protocol
