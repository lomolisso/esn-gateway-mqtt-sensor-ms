import json
import uuid
import logging
from app.subscriber.export import schemas
from app.subscriber.utils import post_to_gateway_api
from app.core.config import (
    GATEWAY_NAME,
    SENSOR_INFERENCE_LAYER,
)

logging.basicConfig(level=logging.INFO)

class ExportHandler:
    def _handle_mqtt_sensor_data(self, sensor_name: str, payload: schemas.SensorData):
        """
        This method handles the MQTT sensor-data export message.
        Note that the inference latency benchmark is exported to the Gateway API if the inference layer is SENSOR_INFERENCE_LAYER
        as the prediction comes with the sensor-data message since it was performed on the sensor.
        """

        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)

        # Step 1: Export Sensor Data to Gateway API
        reading_uuid = payload.reading.uuid
        sensor_data = schemas.SensorDataExport(
            metadata=metadata,
            export_value=payload
        )
        post_to_gateway_api("/export/sensor-data", sensor_data.model_dump())

        # Step 2: Export Inference Latency Benchmark to Gateway API if inference_layer == SENSOR_INFERENCE_LAYER
        _inference_layer = payload.inference_descriptor.inference_layer
        if _inference_layer == SENSOR_INFERENCE_LAYER:
            assert payload.inference_descriptor.prediction is not None

            send_timestamp = payload.inference_descriptor.send_timestamp
            recv_timestamp = payload.inference_descriptor.recv_timestamp
            inference_latency = recv_timestamp - send_timestamp

            inference_latency_benchmark = schemas.InferenceLatencyBenchmarkExport(
                metadata=metadata,
                export_value=schemas.InferenceLatencyBenchmark(
                    sensor_name=sensor_name,
                    inference_layer=_inference_layer,
                    send_timestamp=send_timestamp,
                    recv_timestamp=recv_timestamp,
                    inference_latency=inference_latency
                )
            )
            post_to_gateway_api("/export/inference-latency-benchmark", inference_latency_benchmark.model_dump())            

    def _handle_mqtt_inference_latency_benchmark(self, device_name: str, payload: schemas.InferenceLatencyBenchmark):
        """
        This method handles the MQTT inference-latency-benchmark export message.
        Note this export is only made once a sensor receives an inference-latency-benchmark command message,
        which only happens when the inference layer is CLOUD_INFERENCE_LAYER or GATEWAY_INFERENCE_LAYER.
        """

        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=device_name)
        inference_latency_benchmark = schemas.InferenceLatencyBenchmarkExport(
            metadata=metadata,
            export_value=payload
        )
        post_to_gateway_api("/export/inference-latency-benchmark", inference_latency_benchmark.model_dump())
    
    def handle(self, topic: str, payload: str):
        # export_topic: export/<device_name>/<export_name>
        _, device_name, export_name = topic.split("/")
        payload = json.loads(payload)
        logging.info(f"[MQTT Subscriber] Export from {device_name} for {export_name}")
        
        if export_name == "sensor-data":
            sensor_data = payload
            sensor_data["reading"]["uuid"] = str(uuid.uuid4())
            payload = schemas.SensorData(**sensor_data)
            self._handle_mqtt_sensor_data(device_name, payload)
        elif export_name == "inf-latency-bench":
            payload = schemas.InferenceLatencyBenchmark(**payload)
            self._handle_mqtt_inference_latency_benchmark(device_name, payload)

export_handler = ExportHandler()