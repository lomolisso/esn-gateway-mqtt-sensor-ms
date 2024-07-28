from fastapi import HTTPException, status, APIRouter
import app.api.schemas.command as cmd_schemas
from app.api.utils import send_cmd_to_devices
from app.core.config import LATENCY_BENCHMARK


# --- API Endpoints ---
cmd_router = APIRouter()

@cmd_router.post(
    "/sensor/command/set/sensor-state",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def set_sensor_state(command: cmd_schemas.SetSensorState):
    """
    SET Sensor State Command

    This command is used to set the state of a subset of sensors connected to the edge gateway.
    Among the possible states are: INITIAL, READY, WORKING, IDLE, and ERROR. 

        - INITIAL: When a sensor's state is initial, it will be able to receive and update it's properties,
        such as configuration, inference model, etc.

        - READY: When a sensor's state is ready, it will no longer be able to receive nor update it's properties,
        such as configuration, inference model, etc.
        
        - WORKING: When a sensor's state is working, it will begin to collect data and make inferences if necessary. 

        - IDLE: When a sensor's state is idle, it will cease to collect data and perform inference, essentially
        stopping all operations until it's state is changed.

        - ERROR: When a sensor's state is error, similar to idle, it will cease to collect data and perform inference,
        but it will also require a reset to return to it's initial state. This state is only achieved when, 
        the inference approach selected determines that the industrial equipment associated with the sensor
        is not functioning properly.

    Note that devices DO NOT publish a response for SET commands.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "SET Sensor State Command sent to devices",
        "command_uuids": cmd_uuids
    }


@cmd_router.post(
    "/sensor/command/get/sensor-state",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_sensor_state(command: cmd_schemas.GetSensorState):
    """
    GET Sensor State Command

    This command is used to get the state of a subset of sensors connected to the edge gateway.

    Note that devices DO publish a response for GET commands. Each response will be catched by the device handler
    and sent to the Gateway API for further processing.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "GET Sensor State Command sent to devices",
        "command_uuids": cmd_uuids
    }


@cmd_router.post(
    "/sensor/command/set/sensor-config",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def set_sensor_config(command: cmd_schemas.SetSensorConfig):
    """
    SET Sensor Config Command

    This command is used to set the configuration of a subset of sensors connected to the edge gateway. 
    Currently, the SensorConfig model only contains a sleep_interval_ms attribute, which is used to set the
    time interval between sensor data collection.

    Note that devices DO NOT publish a response for SET commands.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "SET Sensor Config Command sent to devices",
        "command_uuids": cmd_uuids
    }
    

@cmd_router.post(
    "/sensor/command/get/sensor-config",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_sensor_config(command: cmd_schemas.GetSensorConfig):
    """
    GET Sensor Config Command

    This command is used to get the configuration of a subset of sensors connected to the edge gateway.

    Note that devices DO publish a response for GET commands. Each response will be catched by the device handler
    and sent to the Gateway API for further processing.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "GET Sensor Config Command sent to devices",
        "command_uuids": cmd_uuids,
    }


@cmd_router.post(
    "/sensor/command/set/inference-layer",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def set_sensor_inference_layer(command: cmd_schemas.SetInferenceLayer):
    """
    SET Sensor Inference Layer Command

    This command is used to set the inference layer of a subset of sensors connected to the edge gateway.
    The InferenceLayer enum contains three possible values: CLOUD=2, GATEWAY=1, and SENSOR=0.

    Note that devices DO NOT publish a response for SET commands.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "SET Sensor Inference Layer Command sent to devices",
        "command_uuids": cmd_uuids
    }

@cmd_router.post(
    "/sensor/command/get/inference-layer",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_sensor_inference_layer(command: cmd_schemas.GetInferenceLayer):
    """
    GET Sensor Inference Layer Command

    This command is used to get the inference layer of a subset of sensors connected to the edge gateway.

    Note that devices DO publish a response for GET commands. Each response will be catched by the device handler
    and sent to the Gateway API for further processing.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "GET Sensor Inference Layer Command sent to devices",
        "command_uuids": cmd_uuids
    }


@cmd_router.post(
    "/sensor/command/set/sensor-model",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def set_sensor_model(command: cmd_schemas.SetSensorModel):
    """
    SET Sensor Model Command

    This command is used to set the inference model of a subset of sensors connected to the edge gateway.
    The SensorModel model contains two attributes: tf_model_b64 and tf_model_bytesize. The first attribute
    is the base64 encoded bytes of the compressed model using GZIP, while the second attribute is the size
    of the uncompressed model in bytes.
    """
    cmd_uuids = send_cmd_to_devices(command)
    return {
        "message": "Upload Sensor Model Command Sent to Devices",
        "command_uuids": cmd_uuids
    }


@cmd_router.post(
    "/sensor/command/set/inf-latency-bench",
    tags=["Edge Sensor Commands"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def inference_latency_benchmark(
    command: cmd_schemas.InferenceLatencyBenchmarkCommand,
):
    """
    Inference Latency Benchmark Command

    This is an experimental endpoint used to benchmark the inference latency a sensor is experiencing.
    The payload of this command is an InferenceLatencyBenchmark model, which contains two attributes:
    reading_uuid and send_timestamp. The reading_uuid is a unique identifier for the reading being benchmarked,
    while the send_timestamp is the timestamp at which the benchmark was sent. This endpoint has no real-world
    application and should only be used for testing purposes.

    Note that devices DO NOT publish a response for SET commands. However, for this specific command, devices will
    send an Export message containing the payload sent in this command plus the timestamp at which the Export was sent. 
    """
    if LATENCY_BENCHMARK:
        cmd_uuids = send_cmd_to_devices(command)
        return {
            "message": "Inference Latency Benchmark Command Sent to Devices",
            "command_uuids": cmd_uuids,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latency Benchmarking is disabled",
        )
