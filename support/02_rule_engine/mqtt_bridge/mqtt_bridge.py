import json
import logging
import os
import statistics

import paho.mqtt.client as mqtt
import requests

# Setup logging to output standard formats (Docker will capture this perfectly)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables for Docker Compose configurability
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
GORULES_URL = os.getenv("GORULES_URL", "http://localhost:80/evaluate")
GORULES_TOKEN = os.getenv("GORULES_TOKEN", "")
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 5))

logging.info(f"MQTT_BROKER: {MQTT_BROKER}")
logging.info(f"GORULES_URL: {GORULES_URL}")
logging.info(f"GORULES_TOKEN: {GORULES_TOKEN}")
logging.info(f"WINDOW_SIZE: {WINDOW_SIZE}")

SENSOR_TOPIC = "sensors/pico"
ACTION_TOPIC = "actions/pico"

# State to keep track of previous readings
humidity_window = []
temperature_window = []


def format_request(request):
    return (
        f"{request.method} {request.url}\n"
        f"{'\n'.join(f'{k}: {v}' for k, v in request.headers.items())}\n\n"
        f"{request.body if request.body else ''}"
    )


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
        logger.info(f"Successfully connected to MQTT broker at {MQTT_BROKER}")
        client.subscribe(SENSOR_TOPIC)
        logger.info(f"Subscribed to topic: {SENSOR_TOPIC}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")


def on_message(client, _, msg):
    try:
        payload_str = msg.payload.decode("utf-8")
        logger.info(f"Received message on {msg.topic}: {payload_str}")

        data = json.loads(payload_str)

        # Read raw values from the Pico
        h = data.get("humidity")
        t = data.get("temperature")

        if h is None and t is None:
            logger.warning("Received message with neither humidity nor temperature!")

        # Calculate median humidity
        if h is not None:
            humidity_window.append(h)
            if len(humidity_window) > WINDOW_SIZE:
                humidity_window.pop(0)
            data["median_humidity"] = statistics.median(humidity_window)

        # Calculate median temperature
        if t is not None:
            temperature_window.append(t)
            if len(temperature_window) > WINDOW_SIZE:
                temperature_window.pop(0)
            data["median_temperature"] = statistics.median(temperature_window)

        data = {"context": data}

        # Send enriched facts to gorules-brms
        logger.info(f"Sending enriched data to GoRules: {data}")
        headers = {"Content-Type": "application/json", "X-Access-Token": GORULES_TOKEN}
        # Added a timeout so the script doesn't freeze if GoRules is down
        response = requests.post(GORULES_URL, json=data, headers=headers, timeout=5)

        logger.info(f"Request: {format_request(response.request)}")

        if response.status_code == 200:
            logger.info(f"Response text: {response.text}")
            result = response.json().get("result", [])

            if result:
                logger.info(f"Received actions from GoRules: {result}")
                payload_to_send = json.dumps(result)
                client.publish(ACTION_TOPIC, payload_to_send)
                logger.info(f"Published action '{result}' to {ACTION_TOPIC}")
        else:
            logger.error(f"GoRules API Error: {response.status_code} - {response.text}")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from message payload: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error when contacting GoRules: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in on_message: {e}", exc_info=True)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

logger.info(
    f"Starting MQTT Bridge. Broker: {MQTT_BROKER}, GoRules URL: {GORULES_URL}, Window size: {WINDOW_SIZE}"
)

try:
    client.connect(MQTT_BROKER)
    client.loop_forever()
except Exception as e:
    logger.error(f"Failed to start MQTT client: {e}", exc_info=True)
