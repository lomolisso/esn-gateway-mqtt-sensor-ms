from fastapi import HTTPException, status, APIRouter
from app.core.config import GATEWAY_API_URL
import app.api.schemas.response as response_schemas
from app.api.utils import post_to_gateway_api




# --- API Endpoints ---
response_router = APIRouter()

@response_router.post("/sensor/response/get/sensor-state", tags=["Edge Sensor Responses"])
async def get_sensor_state(response: response_schemas.SensorStateResponse):
    """
    GET Sensor State Command Response

    This response is used to get the state of a subset of sensors connected to the edge gateway.
    """

    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/store/sensor/response/get/sensor-state", response.model_dump())
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"message": "GET Sensor State Response sent to Gateway API"}

@response_router.post("/sensor/response/get/sensor-config", tags=["Edge Sensor Responses"])
async def get_sensor_config(response: response_schemas.SensorConfigResponse):
    """
    GET Sensor Config Command Response

    This response is used to get the configuration of a subset of sensors connected to the edge gateway.
    """
    
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/store/sensor/response/get/sensor-config", response.model_dump())
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"message": "GET Sensor Config Response sent to Gateway API"}

@response_router.post("/sensor/response/get/inference-layer", tags=["Edge Sensor Responses"])
async def get_sensor_inference_layer(response: response_schemas.InferenceLayerResponse):
    """
    GET Sensor Inference Layer Command Response

    This response is used to get the inference layer of a subset of sensors connected to the edge gateway.
    """
    
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/store/sensor/response/get/inference-layer", response.model_dump())
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"message": "GET Sensor Inference Layer Response sent to Gateway API"}
