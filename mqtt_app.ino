
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "settings.h"

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
// #define LED_PIN BUILTIN_LED
#define LED_PIN 0

#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int led_status = 0;

void setup_wifi()
{

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, wifi_password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *payload, unsigned int length)
{
  payload[length] = 0;

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println((char *)payload);

  if (String((char *) payload) == "ON")
  {
    digitalWrite(LED_PIN, LOW); // Turn the LED on 
    led_status = 1;
  }
  else
  {
    digitalWrite(LED_PIN, HIGH); // Turn the LED off 
    led_status = 0;
  }

  Serial.println();
  snprintf(msg, MSG_BUFFER_SIZE, "LED %s", led_status > 0 ? "ON" : "OFF");
  Serial.print("Publish message: ");
  Serial.println(msg);
  client.publish(out_topic, msg);
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    const char *client_id = String(random(0xffff), HEX).c_str();
    // Attempt to connect
    if (client.connect(client_id))
    {
      Serial.println("connected");

      client.subscribe(in_topic);
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(115200);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_server_port);
  client.setCallback(callback);

  pinMode(LED_PIN, OUTPUT); // Initialize the LED_PIN pin as an output
  digitalWrite(LED_PIN, HIGH); // Turn the LED off 
}

void loop()
{

  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
}