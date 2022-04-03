import board
import busio
import time
from digitalio import DigitalInOut

from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT

from adafruit_ntp import NTP

import epd2in9

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

# Display
epd = epd2in9.EPD()
epd.init()

# Value Consts
temp_const = "temp"
humidity_const = "humidity"
tvoc_const = "tvoc"
eco2_const = "eco2"

# MQTT Values Dict
mqtt_values = {
    temp_const: -1.0,
    humidity_const: -1.0,
    tvoc_const: -1.0,
    eco2_const: -1.0
}

# Last display set
display_set_interval = 600
display_set_with_data = False
first_data_set_interval = 10

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
    data = "{0} - {1}".format(topic, message)
    print("New Message from MQTT: {0}".format(data))
    if topic == temp_feed:
        mqtt_values[temp_const] = round(float(message),1)
    elif topic == humidity_feed:
        mqtt_values[humidity_const] = round(float(message),1)
    elif topic == tvoc_feed:
        mqtt_values[tvoc_const] = float(message)
    elif topic == eco2_feed:
        mqtt_values[eco2_const] = float(message)

def calc_time():
    now = time.localtime()
    hour = now.tm_hour
    min = now.tm_min
    hourStr = ""
    if hour < 10:
        hourStr = "0"+str(hour)
    else:
        hourStr = str(hour)
    minStr = ""
    if min < 10:
        minStr = "0"+str(min)
    else:
        minStr = str(min) 
    return "{}:{}".format(hourStr,minStr)

def set_display():
    print("Updating display")
    epd.clear_framebuffer()
    temp_val = str(mqtt_values[temp_const]) + "C"
    epd.framebuf.text(temp_val, 10, 10, True, size = 3)
    humidity_val = str(mqtt_values[humidity_const]) + "%H"
    epd.framebuf.text(humidity_val, 160, 10, True, size = 3)
    epd.framebuf.text(tvoc_const, 10, 50, True, size = 3)
    epd.framebuf.text(str(int(mqtt_values[tvoc_const])), 160, 50, True, size = 3)
    epd.framebuf.text(eco2_const, 10, 90, True, size = 3)
    epd.framebuf.text(str(int(mqtt_values[eco2_const])), 160, 90, True, size = 3)
    #epd.framebuf.text(calc_time(), 85, 100, True, size = 3)
    epd.invert_framebuffer()
    epd.display_frame_buf(epd.buffer)

spi = busio.SPI(esp32_sck, esp32_mosi, esp32_miso)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

def check_and_reconnect_wifi():
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
            print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
            print("IP address", esp.pretty_ip(esp.ip_address))
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue

ntp = NTP(esp)
def check_and_reconnect_ntp():
    while not ntp.valid_time:
        time.sleep(1)
        print("Setting time")
        ntp.set_time(7200)

try:
    from secrets import secrets
except ImportError:
    print("secrets not found. Please add them to secrets.py")

print("Clear display...")
epd.clear_frame_memory()
epd.display_frame()
print("Write to display")
set_display()
while True:
    if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        print("ESP32 found and in idle mode")
    print("Firmware vers.", esp.firmware_version)
    print("MAC addr:", [hex(i) for i in esp.MAC_address])

    print("Connecting to AP...")
    check_and_reconnect_wifi()
    check_and_reconnect_ntp()

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

    print("Start MQTT loop...")
    last_display_set = time.time()
    last_first_display_set = time.time()
    killed = False
    while not killed:
        try:
            mqtt_client.loop()
            if (time.time() - last_first_display_set) > first_data_set_interval and not display_set_with_data:
                last_first_display_set = time.time()
                display_set_with_data = True
                set_display()
            if (time.time() - last_display_set) > display_set_interval:
                last_display_set = time.time()
                set_display()
                check_and_reconnect_wifi()
                check_and_reconnect_ntp()
        except Exception:
            killed = True
            continue
        
        time.sleep(1)