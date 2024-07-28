from pydantic import BaseModel
from typing import Optional

# --- Export Payloads ---
class SensorReading(BaseModel):
    uuid: Optional[str] = None
    values: list[list[float]]

class InferenceDescriptor(BaseModel):
    inference_layer: int
    send_timestamp: int
    recv_timestamp: Optional[int] = None
    prediction: Optional[int] = None

class MQTTSensorDataExport(BaseModel):
    low_battery: bool
    sensor_reading: SensorReading
    inference_descriptor: InferenceDescriptor

class MQTTInferenceLatencyBenchmarkExport(BaseModel):
    reading_uuid: str
    send_timestamp: int
    recv_timestamp: int
    inference_latency: int
