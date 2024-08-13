import threading
import logging
import paho.mqtt.client as mqtt
from app.core.config import (
    DEVICE_EXPORT_TOPIC,
    DEVICE_RESPONSE_TOPIC,
)
from app.subscriber.export import export_handler
from app.subscriber.response import response_handler

logging.basicConfig(level=logging.INFO)

# --- MQTT callback functions ---
def on_connect(client, userdata, flags, rc):
    logging.info(f"[MQTT Subscriber] Connected to broker with result code {rc}")
    
    # subscribe to topics
    client.subscribe(DEVICE_EXPORT_TOPIC, qos=0)
    client.subscribe(DEVICE_RESPONSE_TOPIC, qos=1)

def on_message(client, userdata, msg):
    logging.info(f"[MQTT Subscriber] Received message on topic {msg.topic}")
    if msg.topic.startswith(DEVICE_EXPORT_TOPIC[:-1]): # removes the wildcard
        threading.Thread(target=export_handler.handle, args=(msg.topic, msg.payload)).start()
    elif msg.topic.startswith(DEVICE_RESPONSE_TOPIC[:-1]): # removes the wildcard
        threading.Thread(target=response_handler.handle, args=(msg.topic, msg.payload)).start()
    else:
        logging.info(f"[MQTT Subscriber] Unknown topic {msg.topic}")


def launch_mqtt_client(mqtt_broker_host, mqtt_broker_port, mqtt_client_id):
    logging.info("[MQTT Subscriber] Starting MQTT Subscriber")
    client = mqtt.Client(
        client_id=mqtt_client_id,
        protocol=mqtt.MQTTv311,
        clean_session=True,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker_host, mqtt_broker_port)
    client.loop_forever()
