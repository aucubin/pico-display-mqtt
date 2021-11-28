import board
import busio
from digitalio import DigitalInOut

from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Pins
esp32_cs = DigitalInOut(board.GP5)
esp32_ready = DigitalInOut(board.GP20)
esp32_reset = DigitalInOut(board.GP21)
esp32_sck = board.GP18
esp32_mosi = board.GP19
esp32_miso = board.GP4

# MQTT Topics
temp_feed = "weather/aucubin/temp"
humidity_feed = "weather/aucubin/humidity"
tvoc_feed = "weather/aucubin/tvoc"
eco2_feed = "weather/aucubin/eco2"

# MQTT Callback functions
def connected(client, userdata, flags, rc):
    print("Connected to MQTT Broker. Subscribing to topics.")
    client.subscribe(temp_feed)
    client.subscribe(humidity_feed)
    client.subscribe(tvoc_feed)
    client.subscribe(eco2_feed)
    
def disconnected(client, userdata, rc):
    print("Disconnected from MQTT Broker.")
    
def message(client, topic, message):
    print("New Message on topic {0}: {1}".format(topic, message))

spi = busio.SPI(esp32_sck, esp32_mosi, esp32_miso)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

try:
    from secrets import secrets
except ImportError:
    print("secrets not found. Please add them to secrets.py")

while True:
    if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        print("ESP32 found and in idle mode")
    print("Firmware vers.", esp.firmware_version)
    print("MAC addr:", [hex(i) for i in esp.MAC_address])

    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
    print("IP address", esp.pretty_ip(esp.ip_address))

    MQTT.set_socket(socket, esp)

    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
        username=secrets["mqtt_username"],
        password=secrets["mqtt_password"]
        )

    mqtt_client.on_connect = connected
    mqtt_client.on_disconnect = disconnected
    mqtt_client.on_message = message

    print("Start connecting to MQTT broker...")
    mqtt_client.connect()
    
    mqtt_client.loop()