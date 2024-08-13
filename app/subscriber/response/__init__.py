import json
import logging

from app.subscriber.response import schemas
from app.subscriber.utils import post_to_gateway_api
from app.core.config import (
    GATEWAY_NAME,
    SENSOR_INFERENCE_LAYER,
    GATEWAY_INFERENCE_LAYER,
    CLOUD_INFERENCE_LAYER,
)

class ResponseHandler:
    def _handle_mqtt_sensor_config(self, sensor_name: str, payload: schemas.SensorConfig):
        """
        This method handles the MQTT sensor-config response message.
        As any other response, this message is received when a GET command is sent to a sensor.
        """

        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)
        sensor_config = schemas.SensorConfigResponse(
            metadata=metadata,
            property_value=payload
        )
        post_to_gateway_api("/store/sensor/response/get/sensor-config", sensor_config.model_dump())

    def _handle_mqtt_sensor_state(self, sensor_name: str, payload: schemas.SensorConfig):
        """
        This method handles the MQTT sensor-state response message.
        As any other response, this message is received when a GET command is sent to a sensor.
        """

        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)
        sensor_state = schemas.SensorStateResponse(
            metadata=metadata,
            property_value=payload
        )
        post_to_gateway_api("/store/sensor/response/get/sensor-state", sensor_state.model_dump())

    def _handle_mqtt_inference_layer(self, sensor_name: str, payload: schemas.SensorConfig):
        """
        This method handles the MQTT inference-layer response message.
        As any other response, this message is received when a GET command is sent to a sensor.
        """

        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)
        inference_layer = schemas.InferenceLayerResponse(
            metadata=metadata,
            property_value=payload
        )
        post_to_gateway_api("/store/sensor/response/get/inference-layer", inference_layer.model_dump())

    def handle(self, topic: str, payload: str):
        # response_topic: response/<device_name>/<property_name>/<method>/<uuid>
        _, device_name, property_name, method, command_uuid = topic.split("/")
        payload = json.loads(payload)
        logging.info(f"[MQTT Subscriber] Response from {device_name} for {property_name}")

        if method != "get":
            logging.info(f"[MQTT Subscriber] Unknown method {method}")
            return

        if property_name == "sensor-config":
            sensor_config = schemas.SensorConfig(
                sleep_interval_ms=payload["sensor-config"]["sleep_interval_ms"]
            )
            self._handle_sensor_config_response(device_name, command_uuid, sensor_config)
        elif property_name == "inference-layer":
            inference_layer = schemas.InferenceLayer(payload["inference-layer"])
            self._handle_inference_layer_response(device_name, command_uuid, inference_layer)
        elif property_name == "sensor-state":
            sensor_state = schemas.SensorState(payload["sensor-state"])
            self._handle_sensor_state_response(device_name, command_uuid, sensor_state)

response_handler = ResponseHandler()