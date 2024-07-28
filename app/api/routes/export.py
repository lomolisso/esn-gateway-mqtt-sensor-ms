from fastapi import HTTPException, status, APIRouter
from app.core.config import GATEWAY_API_URL
import app.api.schemas.export as export_schemas
from app.api.utils import post_to_gateway_api


# --- API Endpoints ---
export_router = APIRouter()

@export_router.post("/export/sensor-reading", status_code=status.HTTP_202_ACCEPTED)
async def export_sensor_data(sensor_reading: export_schemas.SensorReadingExport):
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/export/sensor-reading", sensor_reading.model_dump())
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {"message": "Sensor Reading Export sent to Gateway API"}
    
@export_router.post("/export/prediction-request", status_code=status.HTTP_202_ACCEPTED)
async def export_prediction_request(prediction_request: export_schemas.PredictionRequestExport):
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/export/prediction-request", prediction_request.model_dump())
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {"message": "Prediction Request Export sent to Gateway API"}

@export_router.post("/export/prediction-result", status_code=status.HTTP_202_ACCEPTED)
async def export_prediction_result(prediction_result: export_schemas.PredictionResultExport):
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/export/prediction-result", prediction_result.model_dump())
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {"message": "Prediction Result Export sent to Gateway API"}  

        
@export_router.post("/export/inference-latency-benchmark", status_code=status.HTTP_202_ACCEPTED)
async def export_inference_latency_benchmark(inf_latency_bench: export_schemas.InferenceLatencyBenchmarkExport):
    response = await post_to_gateway_api(f"{GATEWAY_API_URL}/export/inference-latency-benchmark", inf_latency_bench.model_dump())
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {"message": "Inference Latency Benchmark Export sent to Gateway API"}

   
