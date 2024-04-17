#ifndef SETTINGS_H
#define SETTINGS_H

const char *ssid = "your wifi ssid";
const char *wifi_password = "your wifi password";

const char *mqtt_server = "mqtt server url";
uint16_t mqtt_server_port = 1883; // mqtt port

const char *out_topic = "topic for device status";
const char *in_topic = "topic for device control";

#endif
