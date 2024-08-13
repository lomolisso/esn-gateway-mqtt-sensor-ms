import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY")
MQTT_SENSOR_MICROSERVICE_HOST: str = os.environ.get("MQTT_SENSOR_MICROSERVICE_HOST")
MQTT_SENSOR_MICROSERVICE_PORT: int = int(os.environ.get("MQTT_SENSOR_MICROSERVICE_PORT", "8008"))

CLOUD_INFERENCE_LAYER = 2
GATEWAY_INFERENCE_LAYER = 1
SENSOR_INFERENCE_LAYER = 0

LATENCY_BENCHMARK: int = bool(int(os.environ.get("LATENCY_BENCHMARK", 0)))

MQTT_BROKER_HOST: str = os.environ.get("MQTT_BROKER_HOST")
MQTT_BROKER_PORT: int = int(os.environ.get("MQTT_BROKER_PORT", 1883))
MQTT_PUBLISHER_CLIENT_ID: str = os.environ.get("MQTT_PUBLISHER_CLIENT_ID", "mqtt-sensor-ms-publisher")
MQTT_SUBSCRIBER_CLIENT_ID: str = os.environ.get("MQTT_SUBSCRIBER_CLIENT_ID", "mqtt-sensor-ms-subscriber")

DEVICE_EXPORT_TOPIC: str = os.environ.get("DEVICE_EXPORT_TOPIC", "export/#")
DEVICE_RESPONSE_TOPIC: str = os.environ.get("DEVICE_RESPONSE_TOPIC", "response/#")

# cmd_topic : command/<device_name>/<property_name>/<method>/<uuid>
# response_topic : response/<device_name>/<property_name>/<uuid>
DEVICE_CMD_TOPIC_TEMPLATE: str = os.environ.get("DEVICE_CMD_TOPIC_TEMPLATE", "command/%s/%s/%s/%s")

GATEWAY_API_URL: str = os.environ.get("GATEWAY_API_URL")
GATEWAY_NAME: str = os.environ.get("GATEWAY_NAME")

TIMEZONE: str = os.environ.get("TIMEZONE", "Chile/Continental")

ORIGINS: list = [
    "*"
]
