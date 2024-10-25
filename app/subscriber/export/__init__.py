import json
import uuid
import logging
import zlib
import base64
from app.subscriber.export import schemas
from app.subscriber.utils import post_to_gateway_api
from app.core.config import (
    GATEWAY_NAME,
    SENSOR_INFERENCE_LAYER,
    SEQUENCE_LENGTH,
    SAMPLE_SIZE,
)

logging.basicConfig(level=logging.INFO)

class ExportHandler:
    def _handle_mqtt_sensor_data(self, sensor_name: str, payload: dict):
        """
        This method handles the MQTT sensor-data export message.
        Note that the inference latency benchmark is exported to the Gateway API if the inference layer is SENSOR_INFERENCE_LAYER
        as the prediction comes with the sensor-data message since it was performed on the sensor.
        """

        # --- Decode and Decompress Raw Reading ---
        raw_reading = payload["reading"]
        logging.info(f"Raw Reading: {raw_reading}")
        decoded_reading = base64.b64decode(raw_reading)
        decompressed_reading = zlib.decompress(decoded_reading)

        # --- Parse Decompressed Reading ---
        combine_bytes = lambda msb, lsb: (msb << 8) | lsb
        byte_array = bytearray(decompressed_reading)
        _raw_reading = [
            [
                combine_bytes(byte_array[i], byte_array[i + 1])
                for i in range(j * SAMPLE_SIZE * 2, (j + 1) * SAMPLE_SIZE * 2, 2)
            ]
            for j in range(SEQUENCE_LENGTH)
        ]

        # --- Accelerometer Constants ---
        G_MS2 = 9.80665
        MAX_INT_VALUE_SENSOR = 32768.0
        ACC_RAW_TO_MS2 = (G_MS2 / MAX_INT_VALUE_SENSOR)
        SENSOR_ACC_RANGE = 2 # 8g

        # --- Gyroscope Constants ---
        SENSOR_GYR_RANGE = 250.0
        PI = 3.14159265359
        GYR_RAW_TO_RADS = (PI / 180.0) / MAX_INT_VALUE_SENSOR

        # --- Converters ---
        convert_raw_acc_to_ms2 = lambda raw: (pow(2, SENSOR_ACC_RANGE + 1) * ACC_RAW_TO_MS2) * raw
        convert_raw_gyr_to_rads = lambda raw: SENSOR_GYR_RANGE * GYR_RAW_TO_RADS * raw

        # --- Convert Raw Reading to Physical Values ---
        reading = [
            [
                convert_raw_acc_to_ms2(sample[i]) if i < 3 else convert_raw_gyr_to_rads(sample[i])
                for i in range(len(sample))
            ]
            for sample in _raw_reading
        ]

        # --- Prepare Export Value ---
        _reading = {"uuid": str(uuid.uuid4()), "values": reading}
        _low_battery = payload["low_battery"]
        _inference_descriptor = payload["inference_descriptor"]
        sensor_data = schemas.SensorData(
            reading=schemas.SensorReading(**_reading),
            low_battery=_low_battery,
            inference_descriptor=schemas.InferenceDescriptor(**_inference_descriptor)
        )

        # --- Prepare Metadata ---
        metadata = schemas.Metadata(gateway_name=GATEWAY_NAME, sensor_name=sensor_name)

        # Step 1: Export Sensor Data to Gateway API
        sensor_data_export = schemas.SensorDataExport(
            metadata=metadata,
            export_value=sensor_data
        )
        post_to_gateway_api("/export/sensor-data", sensor_data_export.model_dump())
        
    def _handle_mqtt_inference_latency_benchmark(self, device_name: str, payload: dict):
        """
        This method handles the MQTT inference-latency-benchmark export message.
        Note this export is only made once a sensor receives an inference-latency-benchmark command message,
        which only happens when the inference layer is CLOUD_INFERENCE_LAYER or GATEWAY_INFERENCE_LAYER.
        """
        payload = schemas.InferenceLatencyBenchmark(**payload)
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
            self._handle_mqtt_sensor_data(device_name, payload)
        elif export_name == "inf-latency-bench":
            payload = schemas.InferenceLatencyBenchmark(**payload)
            self._handle_mqtt_inference_latency_benchmark(device_name, payload)

export_handler = ExportHandler()
