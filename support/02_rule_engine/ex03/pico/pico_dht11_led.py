import json
import time
import network
import machine
import dht
from umqtt.simple import MQTTClient
import ntptime  # This imports the ntptime.py file you created

# --- Configuration ---
WIFI_SSID = "TheOffice"        # Change to your Wi-Fi SSID
WIFI_PASSWORD = "8006002030" # Change to your Wi-Fi Password
MQTT_BROKER = "192.168.1.220"           # Change to your broker IP
CLIENT_ID = "pico"
SENSOR_TOPIC = b"sensors/pico"
ACTION_TOPIC = b"actions/pico"

# --- Hardware Setup ---
sensor = dht.DHT22(machine.Pin(22))
led = machine.Pin("LED", machine.Pin.OUT)

# --- Functions ---
def connect_wifi():
    """Connects to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network '{}'...".format(WIFI_SSID))
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print(".", end="")
    print("\nConnected to Wi-Fi!")
    print("Network config:", wlan.ifconfig())

def sync_time():
    """Fetches time from NTP server and sets the Pico's RTC."""
    try:
        print("Synchronizing time with NTP...")
        ntptime.settime()
        # Get local time to display it (UTC by default in MicroPython)
        t = time.localtime()
        print("Time synchronized: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5]))
    except Exception as e:
        print("Failed to sync time with NTP:", e)

def on_action(topic, msg):
    """Callback for incoming MQTT messages."""
    try:
        # 1. Decode bytes to string
        raw_payload = msg.decode("utf-8")
        print(f"Raw message received: {raw_payload}")

        # 2. Parse string into a dictionary
        data = json.loads(raw_payload)
        print(f"Parsed JSON: {data}")

        # 3. Handle logic based on the JSON content
        if data.get("led") == 1:
            led.value(1)
            print("Action: LED ON")
        else:
            led.value(0)
            print("Action: LED OFF")

    except Exception as e:
        print("Error processing received JSON:", e)

# --- Main Execution ---

# 1. Connect to Wi-Fi
connect_wifi()

# 2. Sync Time
sync_time()

# 3. Setup MQTT
print("Connecting to MQTT broker...")
client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.set_callback(on_action)
client.connect()
client.subscribe(ACTION_TOPIC)
print("Connected and subscribed to", ACTION_TOPIC)

# 4. Main Loop
while True:
    try:
        # Trigger the DHT11 sensor read
        sensor.measure()
        h = sensor.humidity()/100.0
        t = sensor.temperature()
        
        # Get the current synchronized time
        now = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(now[0], now[1], now[2], now[3], now[4], now[5])

        # Package temperature, humidity, and timestamp
        payload = json.dumps({
            "humidity": h, 
            "temperature": t,
            "timestamp": timestamp
        })

        # Publish raw data to MQTT
        client.publish(SENSOR_TOPIC, payload)
        print("Published:", payload)

    except Exception as e:
        print("Failed to read from sensor or publish:", e)

    # Check for incoming action (LED toggle)
    try:
        client.check_msg()
    except Exception as e:
        print("MQTT check_msg error:", e)

    time.sleep(2)