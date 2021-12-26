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
- Check that the defined Pins match the Display and the AirLift.
