#!/bin/bash
# Start mqtt_listener.py in the background
python mqtt_listener.py &

# Start the FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port $MQTT_SENSOR_MICROSERVICE_PORT