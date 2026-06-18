#include <WiFi.h>
#include <WiFiUdp.h>
#include <DHT.h>
#include "esp_wifi.h" 

const char* ssid = "C3_NET";
const char* password = "password123";

WiFiUDP udp;
const char* broadcastIP = "192.168.4.255"; 
const int udpPort = 4210;

#define DHTPIN 4 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// New Indicator LED Pins
#define POWER_LED_PIN 5
#define WIFI_LED_PIN 6
#define HEARTBEAT_LED_PIN 8

unsigned long previousMillis = 0;
const long interval = 2000; 

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Initialize LED Pins
  pinMode(POWER_LED_PIN, OUTPUT);
  pinMode(WIFI_LED_PIN, OUTPUT);
  pinMode(HEARTBEAT_LED_PIN, OUTPUT);

  // 1. Turn on the Power LED immediately to show the project is ON
  digitalWrite(POWER_LED_PIN, HIGH);
  digitalWrite(WIFI_LED_PIN, LOW); // Start with Wi-Fi LED off

  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  delay(500);

  WiFi.mode(WIFI_AP);
  esp_wifi_set_max_tx_power(WIFI_POWER_8_5dBm); 
  WiFi.softAP(ssid, password);
  udp.begin(udpPort);
}

void loop() {
  unsigned long currentMillis = millis();

  // Heartbeat LED (Blinks every 500ms)
  if ((currentMillis / 500) % 2 == 0) {
    digitalWrite(HEARTBEAT_LED_PIN, LOW);  
  } else {
    digitalWrite(HEARTBEAT_LED_PIN, HIGH); 
  }

  // Check if any devices are connected to the ESP32 Wi-Fi AP
  // If stations > 0, someone is connected!
  if (WiFi.softAPgetStationNum() > 0) {
    digitalWrite(WIFI_LED_PIN, HIGH); // Turn Wi-Fi LED ON
  } else {
    digitalWrite(WIFI_LED_PIN, LOW);  // Turn Wi-Fi LED OFF
  }

  // Send data over UDP every 2 seconds
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      temperature = 0.0;
      humidity = 0.0;
    }

    String dataString = String(temperature, 1) + "," + String(humidity, 1);
    
    udp.beginPacket(broadcastIP, udpPort);
    udp.print(dataString);
    udp.endPacket();
  }
}