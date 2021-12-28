# CO2_measurement
Some CO2 measurement devices built around a ESP-32

Explanation

There are 3 releases of the CO2 measurement device
All models are programmed in micropython, using asynchronous programming and are connected to internet in order to work in all features

Features:

Connected to a WiFI network

MQTT protocol via test.mosquitto.org broker (default)

Output via display or MQTT protocol at topic CO2

Full programable via MQTT protocol al topic MONITOR

Connected to front end NODE-RED via MSG topic 

TTL output in order to trigger a fan device 

Temperature and humidity sensors built-in

Model 1 is a simple (and bad) devide using a CCS811 sensor. Because CCS811 is not a true CO2 sensor, can be useful only to understand and learn some topics in ESP32, interfacing ans micropython

Model 2 is a true CO2 measurement device using a NDIR sensor (MH-Z19B), a true CO2 sensor. Display is a OLED 128 x 64 using SPI interface

Model 3 is very close to model 2 but it uses a TFT-color display interfaced via I2C and with 128x128 pixels
