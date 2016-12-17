#include <DHT.h>
#include <AuthClient.h>
#include <MicroGear.h>
#include <MQTTClient.h>
#include <SHA1.h>
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <EEPROM.h>
#include <MicroGear.h>

// Example
const char* ssid     = "<SSID>";
const char* password = "<PASSWORD>";

#define APPID       "<APP ID>"
#define GEARKEY     "<APP KEY>"
#define GEARSECRET  "<APP SECRET>"
#define ALIAS       "SmartSensor"

#define DHTPIN        D1
#define DHTTYPE       DHT22
#define REFRESH_RATE  3000

WiFiClient client;
AuthClient *authclient;

DHT dht(DHTPIN, DHTTYPE);

MicroGear microgear(client);

void onMsghandler(char *topic, uint8_t* msg, unsigned int msglen) {
  Serial.print("Incoming message --> ");
  msg[msglen] = '\0';
  Serial.println((char *)msg);
}

void onFoundgear(char *attribute, uint8_t* msg, unsigned int msglen) {
  Serial.print("Found new member --> ");
  for (int i = 0; i < msglen; i++) {
    Serial.print((char)msg[i]);
  }
  Serial.println();
}

void onLostgear(char *attribute, uint8_t* msg, unsigned int msglen) {
  Serial.print("Lost member --> ");
  for (int i = 0; i < msglen; i++) {
    Serial.print((char)msg[i]);
  }
  Serial.println();
}

void onConnected(char *attribute, uint8_t* msg, unsigned int msglen) {
  Serial.println("Connected to NETPIE...");
  microgear.setName(ALIAS);
}

void setup() {

  Serial.begin(115200);
  Serial.println("Starting...");

  dht.begin();
  
  /* Event listener */
  microgear.on(MESSAGE, onMsghandler);
  microgear.on(PRESENT, onFoundgear);
  microgear.on(ABSENT, onLostgear);
  microgear.on(CONNECTED, onConnected);

  if (WiFi.begin(ssid, password)) {
    while (WiFi.status() != WL_CONNECTED) {
      delay(250);
      Serial.print(".");
    }
  }

  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  //uncomment the line below if you want to reset token -->
  //microgear.resetToken();
  microgear.init(GEARKEY, GEARSECRET, ALIAS);
  //microgear.subscribe("/test");
  microgear.connect(APPID);

}

void loop() {
  if (microgear.connected()) {
    Serial.println("connected");
    microgear.loop();
    
    float temp = dht.readTemperature();
    float humid = dht.readHumidity();
    
    if (isnan(temp) || isnan(humid) || temp > 100 || humid > 100) {
      temp = 0.0;
      humid = 0.0;
    }
    
    Serial.println("Temp: " + String(temp) + "\tHumid: " + String(humid));
    microgear.publish("/SmartSensor/temp", temp);
    microgear.publish("/SmartSensor/humid", humid);
  }
  else {
    Serial.println("connection lost, reconnect...");
    microgear.connect(APPID);
    delay(REFRESH_RATE);
  }
  delay(REFRESH_RATE);
}
