"""Midea local x40 message."""

from typing import Any

from midealocal.device import DeviceType
from midealocal.message import MessageBody, MessageRequest, MessageResponse, MessageType

MAX_BLOW_SPEED_LOW_FAN_SPEED = 30


class MessageX40Base(MessageRequest):
    """X40 message base."""

    def __init__(
        self,
        protocol_version: int,
        message_type: int,
        body_type: int,
    ) -> None:
        """Initialize X40 message base."""
        super().__init__(
            device_type=DeviceType.X40,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self) -> bytearray:
        raise NotImplementedError


class MessageQuery(MessageX40Base):
    """X40 message query."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize X40 message query."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01,
        )

    @property
    def _body(self) -> bytearray:
        return bytearray([])


class MessageSet(MessageX40Base):
    """X40 message set."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize X40 message set."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x01,
        )
        self.fields: dict[str, int | bool] = {}
        self.light = False
        self.fan_speed = 0
        self.direction: int
        self.ventilation = False
        self.smelly_sensor = False
        self.anion = False

    def read_field(self, field: str) -> int | bool:
        """X40 message set read field."""
        value = self.fields.get(field, 0)
        return value if value else 0

    @property
    def _body(self) -> bytearray:
        light = 1 if self.light else 0
        blow = 1 if self.fan_speed > 0 else 0
        fan_speed = 0xFF if self.fan_speed == 0 else 30 if self.fan_speed == 1 else 100
        ventilation = 1 if self.ventilation else 0
        direction = self.direction
        anion = 1 if self.anion else 0
        smelly_sensor = 1 if self.smelly_sensor else 0
        return bytearray(
            [
                light,
                self.read_field("MAIN_LIGHT_BRIGHTNESS"),
                self.read_field("NIGHT_LIGHT_ENABLE"),
                self.read_field("NIGHT_LIGHT_BRIGHTNESS"),
                self.read_field("RADAR_INDUCTION_ENABLE"),
                self.read_field("RADAR_INDUCTION_CLOSING_TIME"),
                self.read_field("LIGHT_INTENSITY_THRESHOLD"),
                self.read_field("RADAR_SENSITIVITY"),
                self.read_field("HEATING_ENABLE"),
                self.read_field("HEATING_TEMPERATURE"),
                self.read_field("HEATING_SPEED"),
                self.read_field("HEATING_DIRECTION"),
                self.read_field("BATH_ENABLE"),
                self.read_field("BATH_HEATING_TIME"),
                self.read_field("BATH_TEMPERATURE"),
                self.read_field("BATH_SPEED"),
                self.read_field("BATH_DIRECTION"),
                ventilation,
                self.read_field("VENTILATION_SPEED"),
                self.read_field("VENTILATION_DIRECTION"),
                self.read_field("DRYING_ENABLE"),
                self.read_field("DRYING_TIME"),
                self.read_field("DRYING_TEMPERATURE"),
                self.read_field("DRYING_SPEED"),
                self.read_field("DRYING_DIRECTION"),
                blow,
                fan_speed,
                direction,
                self.read_field("DELAY_ENABLE"),
                self.read_field("DELAY_TIME"),
                self.read_field("SOFT_WIND_ENABLE"),
                self.read_field("SOFT_WIND_TIME"),
                self.read_field("SOFT_WIND_TEMPERATURE"),
                self.read_field("SOFT_WIND_SPEED"),
                self.read_field("SOFT_WIND_DIRECTION"),
                self.read_field("WINDLESS_ENABLE"),
                anion,
                smelly_sensor,
                self.read_field("SMELLY_THRESHOLD"),
            ],
        )


class MessageX40Body(MessageBody):
    """X40 message body."""

    def __init__(self, body: bytearray) -> None:
        """Initialize X40 message body."""
        super().__init__(body)
        self.fields = {}
        self.light = body[1] > 0
        self.fields["MAIN_LIGHT_BRIGHTNESS"] = body[2]
        self.fields["NIGHT_LIGHT_ENABLE"] = body[3]
        self.fields["NIGHT_LIGHT_BRIGHTNESS"] = body[4]
        self.fields["RADAR_INDUCTION_ENABLE"] = body[5]
        self.fields["RADAR_INDUCTION_CLOSING_TIME"] = body[6]
        self.fields["LIGHT_INTENSITY_THRESHOLD"] = body[7]
        self.fields["RADAR_SENSITIVITY"] = body[8]
        self.fields["HEATING_ENABLE"] = body[9]
        self.fields["HEATING_TEMPERATURE"] = body[10]
        self.fields["HEATING_SPEED"] = body[11]
        self.fields["HEATING_DIRECTION"] = body[12]
        self.fields["BATH_ENABLE"] = body[13] > 0
        self.fields["BATH_HEATING_TIME"] = body[14]
        self.fields["BATH_TEMPERATURE"] = body[15]
        self.fields["BATH_SPEED"] = body[16]
        self.fields["BATH_DIRECTION"] = body[17]
        self.ventilation = body[18] > 0
        self.fields["VENTILATION_SPEED"] = body[19]
        self.fields["VENTILATION_DIRECTION"] = body[20]
        self.fields["DRYING_ENABLE"] = body[21] > 0
        self.fields["DRYING_TIME"] = body[22]
        self.fields["DRYING_TEMPERATURE"] = body[23]
        self.fields["DRYING_SPEED"] = body[24]
        self.fields["DRYING_DIRECTION"] = body[25]
        blow = body[26] > 0
        blow_speed = body[27]
        self.direction = body[28]
        self.fields["DELAY_ENABLE"] = body[29]
        self.fields["DELAY_TIME"] = body[30]
        self.current_temperature = body[33]
        self.fields["SOFT_WIND_ENABLE"] = body[38]
        self.fields["SOFT_WIND_TIME"] = body[39]
        self.fields["SOFT_WIND_TEMPERATURE"] = body[40]
        self.fields["SOFT_WIND_SPEED"] = body[41]
        self.fields["SOFT_WIND_DIRECTION"] = body[42]
        self.fields["WINDLESS_ENABLE"] = body[43]
        self.anion = body[44] > 0
        self.smelly_sensor = body[45]
        self.fields["SMELLY_THRESHOLD"] = body[46]
        if blow:
            if blow_speed <= MAX_BLOW_SPEED_LOW_FAN_SPEED:
                self.fan_speed = 1
            else:
                self.fan_speed = 2
        else:
            self.fan_speed = 0


class MessageX40Response(MessageResponse):
    """X40 message response."""

    def __init__(self, message: bytes) -> None:
        """Initialize X40 message response."""
        super().__init__(bytearray(message))
        if (
            self.message_type
            in [MessageType.set, MessageType.notify1, MessageType.query]
            and self.body_type == 0x01
        ):
            self.set_body(MessageX40Body(super().body))
        self.fields: dict[str, Any]
        self.set_attr()
