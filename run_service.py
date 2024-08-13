"""
Script that runs both publisher and subscriber
on two separate processes.
"""

import multiprocessing
from app.core.config import (MQTT_SENSOR_MICROSERVICE_HOST, MQTT_SENSOR_MICROSERVICE_PORT, MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_SUBSCRIBER_CLIENT_ID)
from app.publisher.run import run_publisher_process
from app.subscriber.run import run_subscriber_process


def run_publisher():
	run_publisher_process(MQTT_SENSOR_MICROSERVICE_HOST, MQTT_SENSOR_MICROSERVICE_PORT)

def run_subscriber():
	run_subscriber_process(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

if __name__ == "__main__":
	publisher_process = multiprocessing.Process(target=run_publisher)
	subscriber_process = multiprocessing.Process(target=run_subscriber)

	publisher_process.start()
	subscriber_process.start()

	publisher_process.join()
	subscriber_process.join()

