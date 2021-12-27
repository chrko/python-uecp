import asyncio
import logging

import attr

from uecp.commands import (
    DataSetSelectCommand,
    MessageAcknowledgementCommand,
    RDSEnabledSetCommand,
    RequestCommand,
    ResponseCode,
    UECPCommand,
)
from uecp.frame import UECPFrame
from uecp.serial_con.protocol import open_serial_protocol, UECPSerialProtocol


@attr.s(
    auto_detect=True,
    repr=True,
    order=False,
    hash=False,
    kw_only=True,
)
class GenericRDSEncoderState:
    active_data_set: int = attr.ib(
        converter=int, validator=attr.validators.in_(range(1, 9))
    )
    rds_enabled: bool = attr.ib(default=True, converter=bool)

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__qualname__)

    @classmethod
    async def init_from_device(
        cls, proto: UECPSerialProtocol
    ) -> "GenericRDSEncoderState":
        logger = logging.getLogger(cls.__qualname__)

        event_connection_made = asyncio.Event()
        event_all_data_received = asyncio.Event()
        proto.connection_made_callbacks.append(event_connection_made.set)

        state_dict = {}

        def frame_callback(received_frame: UECPFrame):
            for cmd in received_frame.commands:
                if isinstance(cmd, MessageAcknowledgementCommand):
                    if cmd.code is ResponseCode.OK:
                        logger.info("Last frame / cmd successfully transmitted")
                    else:
                        raise Exception(
                            "Error received as response from rds encoder", cmd
                        )
                elif isinstance(cmd, DataSetSelectCommand):
                    logger.info(f"DataSetSelectCommand received {cmd}")
                    state_dict["active_data_set"] = cmd.select_data_set_number
                elif isinstance(cmd, RDSEnabledSetCommand):
                    logger.info(f"RDSEnabledSetCommand received {cmd}")
                    state_dict["rds_enabled"] = cmd.enable
                else:
                    logger.warning("Unknown cmd received {cmd}")

            if state_dict.keys() == attr.fields_dict(cls).keys():
                event_all_data_received.set()

        proto.received_frame_callbacks.append(frame_callback)

        frame = UECPFrame(
            commands=[
                RequestCommand(command=DataSetSelectCommand),
                RequestCommand(command=RDSEnabledSetCommand),
            ]
        )
        if not proto.connected:
            await event_connection_made.wait()
        proto.connection_made_callbacks.remove(event_connection_made.set)
        proto.write(frame)
        await event_all_data_received.wait()
        proto.received_frame_callbacks.remove(frame_callback)
        current = GenericRDSEncoderState(**state_dict)

        return current

    @property
    def refresh_frames(self) -> list[UECPFrame]:
        frame = UECPFrame(
            commands=[
                RequestCommand(command=DataSetSelectCommand),
                RequestCommand(command=RDSEnabledSetCommand),
            ]
        )

        return [frame]

    def receive_frame_callback(self, received_frame: UECPFrame):
        for cmd in received_frame.commands:
            if isinstance(cmd, MessageAcknowledgementCommand):
                if cmd.code is ResponseCode.OK:
                    self.logger.info("Last frame / cmd successfully transmitted")
                else:
                    raise Exception("Error received as response from rds encoder", cmd)
            elif isinstance(cmd, DataSetSelectCommand):
                self.logger.info(f"DataSetSelectCommand received {cmd}")
                self.active_data_set = cmd.select_data_set_number
            elif isinstance(cmd, RDSEnabledSetCommand):
                self.logger.info(f"RDSEnabledSetCommand received {cmd}")
                self.rds_enabled = cmd.enable
            else:
                self.logger.warning("Unknown cmd received {cmd}")

    @staticmethod
    def compare_and_generate(
        current: "GenericRDSEncoderState", target: "GenericRDSEncoderState"
    ) -> list[UECPFrame]:
        cmds: list[UECPCommand] = []
        if current == target:
            return []

        if current.active_data_set != target.active_data_set:
            cmds.append(
                DataSetSelectCommand(select_data_set_number=target.active_data_set)
            )
        if current.rds_enabled != target.rds_enabled:
            cmds.append(RDSEnabledSetCommand(enable=target.rds_enabled))

        frames: list[UECPFrame] = []
        current_frame = UECPFrame()
        for cmd in cmds:
            try:
                current_frame.add_command(cmd)
            except OverflowError:
                frames.append(current_frame)
                current_frame = UECPFrame()
                current_frame.add_command(cmd)

        if len(current_frame.commands) > 0:
            frames.append(current_frame)

        return frames


class GenericRDSEncoder:
    def __init__(self, protocol: UECPSerialProtocol, current: GenericRDSEncoderState):
        self.logger = logging.getLogger(self.__class__.__qualname__)
        self._active_data_set: int = 0
        self._protocol: UECPSerialProtocol = protocol

        self._current = current
        self._target = attr.evolve(current)
        self._protocol.received_frame_callbacks.append(
            self._current.receive_frame_callback
        )

    @classmethod
    async def create(cls, port: str, baudrate: int) -> "GenericRDSEncoder":
        proto = await open_serial_protocol(port, baudrate)
        current = await GenericRDSEncoderState.init_from_device(proto)

        self = cls(proto, current)

        return self

    @property
    def state(self) -> GenericRDSEncoderState:
        return self._target

    @state.setter
    def state(self, value: GenericRDSEncoderState):
        self._target = value

    def ensure_current(self):
        frames = GenericRDSEncoderState.compare_and_generate(
            self._current, self._target
        )
        if len(frames) > 0:
            for frame in frames:
                self._protocol.write(frame)
