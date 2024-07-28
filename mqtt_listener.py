import logging
import json
import uuid
import httpx
import paho.mqtt.client as mqtt
from app.core.config import (
    CLOUD_INFERENCE_LAYER,
    GATEWAY_INFERENCE_LAYER,
    SENSOR_INFERENCE_LAYER,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_SUBSCRIBER_CLIENT_ID,
    DEVICE_EXPORT_TOPIC,
    DEVICE_RESPONSE_TOPIC,
    MQTT_SENSOR_MICROSERVICE_HOST,
    MQTT_SENSOR_MICROSERVICE_PORT,
    GATEWAY_NAME
)
from app.api.schemas import export as export_schemas
from app.api.schemas import response as resp_schemas
from app.api.schemas.mqtt import MQTTSensorDataExport, MQTTInferenceLatencyBenchmarkExport

MQTT_SENSOR_MICROSERVICE_URL = f"http://{MQTT_SENSOR_MICROSERVICE_HOST}:{MQTT_SENSOR_MICROSERVICE_PORT}"

logging.basicConfig(level=logging.INFO)

# --- Utility functions ---
def handle_mqtt_inference_latency_benchmark_export(sensor_name: str, payload: MQTTInferenceLatencyBenchmarkExport):
    payload = MQTTInferenceLatencyBenchmarkExport(**payload)
    metadata = export_schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)
    inference_latency_benchmark = export_schemas.InferenceLatencyBenchmarkExport(
        metadata=metadata,
        export_value=export_schemas.InferenceLatencyBenchmark(
            reading_uuid=payload.reading_uuid,
            send_timestamp=payload.send_timestamp,
            recv_timestamp=payload.recv_timestamp,
            inference_latency=payload.inference_latency
        )
    )
    httpx.post(
        url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/export/inference-latency-benchmark",
        json=inference_latency_benchmark.model_dump()
    )


def handle_mqtt_sensor_data_export(sensor_name: str, payload: dict):
    payload = MQTTSensorDataExport(**payload)
    metadata = export_schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)

    # Step 1: Sensor Reading
    reading_uuid = str(uuid.uuid4())
    sensor_reading = export_schemas.SensorReadingExport(
        metadata=metadata,
        export_value=export_schemas.SensorReading(
            uuid=reading_uuid,
            values=payload.sensor_reading.values
        )
    )
    httpx.post(
        url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/export/sensor-reading",
        json=sensor_reading.model_dump()
    )

    # Step 2: Prediction Request for Cloud or Gateway
    inference_layer = payload.inference_descriptor.inference_layer
    if inference_layer == CLOUD_INFERENCE_LAYER or inference_layer == GATEWAY_INFERENCE_LAYER:
        prediction_request = export_schemas.PredictionRequestExport(
            metadata=metadata,
            export_value=export_schemas.PredictionRequest(
                low_battery=payload.low_battery,
                reading=export_schemas.SensorReading(
                    uuid=reading_uuid,
                    values=payload.sensor_reading.values
                ),
                inference_descriptor=export_schemas.InferenceDescriptor(
                    inference_layer=inference_layer,
                    send_timestamp=payload.inference_descriptor.send_timestamp
                )
            )
        )
        httpx.post(
            url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/export/prediction-request",
            json=prediction_request.model_dump()
        )
        return
    
    # Step 3: Prediction Result when inference_layer == SENSOR_INFERENCE_LAYER
    if inference_layer == SENSOR_INFERENCE_LAYER:
        # Step 3.1: Send Prediction Result to Sensor Microservice
        prediction_result = export_schemas.PredictionResultExport(
            metadata=metadata,
            export_value=export_schemas.PredictionResult(
                reading_uuid=reading_uuid,
                send_timestamp=payload.inference_descriptor.send_timestamp,
                prediction=payload.inference_descriptor.prediction,
                inference_layer=inference_layer
            )
        )
        httpx.post(
            url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/export/prediction-result",
            json=prediction_result.model_dump()
        )

        # Step 3.2: Send Inference Latency Benchmark to Sensor Microservice
        inference_latency_benchmark = export_schemas.InferenceLatencyBenchmarkExport(
            metadata=metadata,
            export_value=export_schemas.InferenceLatencyBenchmark(
                reading_uuid=reading_uuid,
                send_timestamp=payload.inference_descriptor.send_timestamp,
                recv_timestamp=payload.inference_descriptor.recv_timestamp,
                inference_latency=payload.inference_descriptor.recv_timestamp - payload.inference_descriptor.send_timestamp
            )
        )
        httpx.post(
            url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/export/inference-latency-benchmark",
            json=inference_latency_benchmark.model_dump()
        )
        return


def device_export_message_recv(topic, payload):
    # export_topic: export/<device_name>/<export_name>
    _, device_name, export_name = topic.split("/")
    payload = json.loads(payload)
    logging.info(f"[MQTT Subscriber] Export from {device_name} for {export_name}")
    
    if export_name == "sensor-data":
        handle_mqtt_sensor_data_export(device_name, payload)
    elif export_name == "inf-latency-bench":
        handle_mqtt_inference_latency_benchmark_export(device_name, payload)

def handle_sensor_config_response(device_name, command_uuid, payload):
    response = resp_schemas.SensorConfigResponse(
        metadata=resp_schemas.Metadata(
            sender=device_name,
            command_uuid=command_uuid
        ),
        resource_value=resp_schemas.SensorConfig(
            sleep_interval_ms=payload["sensor-config"]["sleep_interval_ms"]
        )
    )
    httpx.post(
        url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/sensor/response/get/sensor-config",
        json=response.model_dump()
    )

def handle_inference_layer_response(device_name, command_uuid, payload):
    response = resp_schemas.InferenceLayerResponse(
        metadata=resp_schemas.Metadata(
            sender=device_name,
            command_uuid=command_uuid
        ),
        resource_value=resp_schemas.InferenceLayer(payload["inference-layer"])
    )
    httpx.post(
        url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/sensor/response/get/inference-layer",
        json=response.model_dump()
    )

def handle_sensor_state_response(device_name, command_uuid, payload):
    response = resp_schemas.SensorStateResponse(
        metadata=resp_schemas.Metadata(
            sender=device_name,
            command_uuid=command_uuid
        ),
        resource_value=resp_schemas.SensorState(payload["sensor-state"])
    )
    httpx.post(
        url=f"{MQTT_SENSOR_MICROSERVICE_URL}/api/v1/sensor/response/get/sensor-state",
        json=response.model_dump()
    )

def device_response_message_recv(topic, payload):
    # response_topic: response/<device_name>/<resource_name>/<method>/<uuid>
    _, device_name, resource_name, method, command_uuid = topic.split("/")
    payload = json.loads(payload)
    logging.info(f"[MQTT Subscriber] Response from {device_name} for {resource_name}")

    if method != "get":
        logging.info(f"[MQTT Subscriber] Unknown method {method}")
        return

    if resource_name == "sensor-config":
        handle_sensor_config_response(device_name, command_uuid, payload)
    elif resource_name == "inference-layer":
        handle_inference_layer_response(device_name, command_uuid, payload)
    elif resource_name == "sensor-state":
        handle_sensor_state_response(device_name, command_uuid, payload)


# --- MQTT callback functions ---
def on_connect(client, userdata, flags, rc):
    logging.info(f"[MQTT Subscriber] Connected to broker with result code {rc}")
    
    # subscribe to topics
    client.subscribe(DEVICE_EXPORT_TOPIC, qos=0)
    client.subscribe(DEVICE_RESPONSE_TOPIC, qos=1)

def on_message(client, userdata, msg):
    logging.info(f"[MQTT Subscriber] Received message on topic {msg.topic}")
    if msg.topic.startswith(DEVICE_EXPORT_TOPIC[:-1]): # removes the wildcard
        device_export_message_recv(msg.topic, msg.payload)
    elif msg.topic.startswith(DEVICE_RESPONSE_TOPIC[:-1]): # removes the wildcard
        device_response_message_recv(msg.topic, msg.payload)
    else:
        logging.info(f"[MQTT Subscriber] Unknown topic {msg.topic}")

logging.info("[MQTT Subscriber] Starting MQTT Subscriber")
client = mqtt.Client(
    client_id=MQTT_SUBSCRIBER_CLIENT_ID,
    protocol=mqtt.MQTTv311,
    clean_session=True,
    
)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
client.loop_forever()
