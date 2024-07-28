import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT
from gmqtt.mqtt.constants import MQTTv311
from app.core.config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_PUBLISHER_CLIENT_ID,
)

# --- Init FastMQTT ---
mqtt_router = FastMQTT(
    config=MQTTConfig(
        host=MQTT_BROKER_HOST,
        port=MQTT_BROKER_PORT,
        version=MQTTv311
    ),
    client_id=MQTT_PUBLISHER_CLIENT_ID,
    clean_session=False
)


@asynccontextmanager
async def mqtt_lifespan(app: FastAPI):
    await mqtt_router.mqtt_startup()
    yield
    await mqtt_router.mqtt_shutdown()


# --- MQTT Client ---
@mqtt_router.on_connect()
def connect(client, flags, rc, properties):
    print("Connected: ", client, flags, rc, properties)

@mqtt_router.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")
