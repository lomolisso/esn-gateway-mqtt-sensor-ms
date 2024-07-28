import uuid
import json
import httpx
from app.api.schemas import command as cmd_schemas
from app.core.config import DEVICE_CMD_TOPIC_TEMPLATE
from app.mqtt import mqtt_router

async def post_to_gateway_api(url: str, json_data: dict):
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=json_data)

def send_cmd_to_devices(command: cmd_schemas.BaseCommand):
    target = command.target.target_sensors
    cmd_uuids = [str(uuid.uuid4()) for _ in target]
    for cmd_uuid, cmd_target in zip(cmd_uuids, target):
        cmd_method = command.method.value
        cmd_resource_name = command.resource_name
        cmd_payload = command.to_mqtt()
               
        # create command topic
        # cmd_topic : command/<device_name>/<resource_name>/<method>/<uuid>
        cmd_topic = DEVICE_CMD_TOPIC_TEMPLATE % (cmd_target, cmd_resource_name, cmd_method, cmd_uuid)
        cmd_payload = json.dumps(cmd_payload)

        # publish command to broker
        mqtt_router.client.publish(cmd_topic, cmd_payload, qos=1, retain=False)
        print(f"[MQTT Publisher] Command sent to topic {cmd_topic}")
    
    return cmd_uuids