FROM python:3.10

# requirements for app are installed
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip install -r /tmp/requirements.txt

# run backend app
WORKDIR /app
EXPOSE $MQTT_SENSOR_MICROSERVICE_PORT
CMD python3 run_service.py