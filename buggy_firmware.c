#include <Arduino.h>
#include <string.h>

String deviceName = "sensor-node";
char message[8];

volatile int pulseCount = 0;

void onPulse() {
    pulseCount++;
}

void setup() {
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(2), onPulse, RISING);
    strcpy(message, "temperature");
}

void loop() {
    Serial.println(deviceName);
    delay(1000);
}
