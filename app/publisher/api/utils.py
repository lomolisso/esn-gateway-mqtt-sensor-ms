import uuid
import json

from fastapi_mqtt import FastMQTT
from app.publisher.api import schemas as schemas
from app.core.config import DEVICE_CMD_TOPIC_TEMPLATE

def send_cmd_to_devices(fast_mqtt: FastMQTT, command: schemas.BaseCommand):
    target = command.target.target_sensors
    cmd_uuids = [str(uuid.uuid4()) for _ in target]
    for cmd_uuid, cmd_target in zip(cmd_uuids, target):
        cmd_method = command.method.value
        cmd_property_name = command.property_name
        cmd_payload = command.to_mqtt()
               
        # create command topic
        # cmd_topic : command/<device_name>/<property_name>/<method>/<uuid>
        cmd_topic = DEVICE_CMD_TOPIC_TEMPLATE % (cmd_target, cmd_property_name, cmd_method, cmd_uuid)
        cmd_payload = json.dumps(cmd_payload)

        # publish command to broker
        print(f"[MQTT Publisher] Command sent to topic {cmd_topic}")
        fast_mqtt.client.publish(cmd_topic, cmd_payload, qos=1, retain=False)
    
    return cmd_uuids