from app.subscriber import mqtt_client

def run_subscriber_process(mqtt_broker_host, mqtt_broker_port):
    mqtt_client.connect(mqtt_broker_host, mqtt_broker_port)
    mqtt_client.loop_forever()
