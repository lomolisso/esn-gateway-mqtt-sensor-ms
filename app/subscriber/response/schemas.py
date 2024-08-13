import enum
from pydantic import BaseModel
from typing import Optional


class Metadata(BaseModel):
    """
    Metadata for the response
    """

    sender: str
    command_uuid: str


class Method(str, enum.Enum):
    GET = "get"
    SET = "set"


class SensorState(str, enum.Enum):
    INITIAL = "initial"
    UNLOCKED = "unlocked"
    LOCKED = "locked"
    WORKING = "working"
    IDLE = "idle"
    ERROR = "error"


class InferenceLayer(int, enum.Enum):
    CLOUD = 2
    GATEWAY = 1
    SENSOR = 0


class SensorConfig(BaseModel):
    sleep_interval_ms: int


class BaseResponse(BaseModel):
    metadata: Metadata
    property_name: Optional[str] = None
    property_value: object = None
    method: Method = Method.GET


class SensorConfigResponse(BaseResponse):
    property_name: str = "sensor-config"
    property_value: SensorConfig


class InferenceLayerResponse(BaseResponse):
    property_name: str = "inference-layer"
    property_value: InferenceLayer


class SensorStateResponse(BaseResponse):
    property_name: str = "sensor-state"
    property_value: SensorState
