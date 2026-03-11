FROM python:3.12-alpine
WORKDIR /app
COPY mqtt_bridge.py .
RUN pip install paho-mqtt requests
CMD ["python", "mqtt_bridge.py"]
