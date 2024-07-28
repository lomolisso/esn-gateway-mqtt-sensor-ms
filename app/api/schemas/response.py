from pydantic import BaseModel
from app.api.schemas.command import SensorConfig, InferenceLayer, SensorState, Method
from typing import Optional

class Metadata(BaseModel):
    """
    Metadata for the response
    """

    sender: str
    command_uuid: str

class BaseResponse(BaseModel):
    metadata: Metadata
    resource_name: Optional[str] = None
    resource_value: object = None
    method: Method = Method.GET

class SensorConfigResponse(BaseResponse):
    resource_name: str = "sensor-config"
    resource_value: SensorConfig

class InferenceLayerResponse(BaseResponse):
    resource_name: str = "inference-layer"
    resource_value: InferenceLayer

class SensorStateResponse(BaseResponse):
    resource_name: str = "sensor-state"
    resource_value: SensorState

class ResponseFactory:
    @staticmethod
    def create_response(resource_name: str, **kwargs):
        if resource_name == "sensor-config":
            return SensorConfigResponse(**kwargs)
        elif resource_name == "inference-layer":
            return InferenceLayerResponse(**kwargs)
        elif resource_name == "sensor-state":
            return SensorStateResponse(**kwargs)
        else:
            print(f"Unknown resource name {resource_name}")
            return None
