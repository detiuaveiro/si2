# mqtt_bridge: Python MQTT to gorules-brms Bridge

## Purpose
- Subscribes to MQTT sensor topic (`sensors/pico1`)
- Sends sensor data to gorules-brms REST API
- Publishes actions (LED_ON/LED_OFF) to MQTT action topic (`actions/pico1`)

## Usage
- Build with Docker Compose
- Configure environment variables as needed

## Files
- mqtt_bridge.py: Main bridge script
- Dockerfile: Container build instructions
