# Pico-Display-MQTT
Displays data from MQTT on the Waveshare 2.9" E-Paper Display (written in CircuitPython)

# Required Parts
- Raspberry Pi Pico
- Adafruit Airlift
- Waveshare Pico-CapTouch-ePaper-2.9 

# Building
- Flash CircuitPython Firmware if not installed yet on the Pico
- Add the required libraries to the Pico in the lib folder:
    - Adafruit MiniMQTT
    - Adafruit NTP
    - Adafruit ESP32 SPI
    - Adafruit Framebuf
    - Adafruit Bus Device
- Create a secrets.py file which contains a dictionary secrets with the credentials for WiFi and the MQTT broker. You can copy the secrets.template.py from the repo.
- Check that the defined Pins match the Displays and the AirLift.

# Licenses
The epd2in9.py and epdif.py are initially from [this](https://github.com/gpshead/epaper-circuitpython/tree/master/third_party/waveshare) repository and have been modified to work with the Pico-CapTouch-ePaper-2.9 with the use of the [sample waveshare code](https://github.com/waveshare/Pico_CapTouch_ePaper/blob/main/python/Pico_CapTouch_ePaper_Test_2in9.py). As both of these dependencies use the MIT license this modified code also uses the MIT license (see LICENSE file and the Copyright notices in the epd2in9.py/epdif.py).
