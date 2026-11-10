// Silver Back sensor firmware 0.1.0
//
// Reads a digital presence pin and writes one JSON object per line on USB
// serial. The line format is docs/protocol.md. This sketch does not speak
// BLE or Wi-Fi, and it does not sleep.
//
// Reference wiring (ESP32 dev board + HC-SR501):
//   GPIO 27  <-- OUT     (internal pulldown; HIGH means approach)
//   GND      --- GND
//   5V / VIN --> VCC     (the module wants about 5 V)
// Confirm OUT is 3.3 V before connecting it. ESP32 pins are not 5 V tolerant.
// HC-SR501 can chatter for up to a minute after power-up. Warmup suppression
// is not implemented; those edges are reported as real events.
//
// The strings below are fixed tokens. Nothing from the pin is copied into
// the JSON text, so the line stays valid JSON.

#include <Arduino.h>

#ifndef SILVERBACK_PIR_PIN
#define SILVERBACK_PIR_PIN 27
#endif

#ifndef SILVERBACK_LED_PIN
#define SILVERBACK_LED_PIN 2
#endif

#ifndef SILVERBACK_PIR_ACTIVE
#define SILVERBACK_PIR_ACTIVE HIGH
#endif

static const char *FW_VERSION = "0.1.0";
static const uint32_t BAUD = 115200;
static const unsigned long DEBOUNCE_MS = 200;
static const unsigned long HEARTBEAT_MS = 30000;

static int lastReading = LOW;
static int stable = -1;
static unsigned long lastChangeMs = 0;
static unsigned long lastHeartbeatMs = 0;
static uint32_t seq = 0;

static void emit(const char *type, const char *state) {
  Serial.print(F("{\"v\":1,\"type\":\""));
  Serial.print(type);
  Serial.print('"');
  if (state != nullptr) {
    Serial.print(F(",\"state\":\""));
    Serial.print(state);
    Serial.print('"');
  }
  Serial.print(F(",\"sensor\":\"pir\",\"transport\":\"usb-serial\",\"fw\":\""));
  Serial.print(FW_VERSION);
  Serial.print(F("\",\"seq\":"));
  Serial.print(seq++);
  Serial.print(F(",\"uptime_ms\":"));
  Serial.print(millis());
  Serial.println('}');
  Serial.flush();
}

static void setLed(bool occupied) {
  if (SILVERBACK_LED_PIN < 0) {
    return;
  }
  digitalWrite(SILVERBACK_LED_PIN, occupied ? HIGH : LOW);
}

void setup() {
  if (SILVERBACK_LED_PIN >= 0) {
    pinMode(SILVERBACK_LED_PIN, OUTPUT);
    digitalWrite(SILVERBACK_LED_PIN, LOW);
  }
  pinMode(SILVERBACK_PIR_PIN, INPUT_PULLDOWN);
  Serial.begin(BAUD);
  lastReading = digitalRead(SILVERBACK_PIR_PIN);
  lastChangeMs = millis();
  lastHeartbeatMs = millis();
  emit("hello", nullptr);
}

void loop() {
  const unsigned long now = millis();
  const int reading = digitalRead(SILVERBACK_PIR_PIN);

  if (reading != lastReading) {
    lastReading = reading;
    lastChangeMs = now;
  }

  // Emit on the transition to a level that has held for DEBOUNCE_MS,
  // including the level seen at boot (stable starts unknown).
  if (stable != reading && (now - lastChangeMs) >= DEBOUNCE_MS) {
    stable = reading;
    const bool occupied = reading == SILVERBACK_PIR_ACTIVE;
    setLed(occupied);
    emit("presence", occupied ? "approach" : "clear");
  }

  if ((now - lastHeartbeatMs) >= HEARTBEAT_MS) {
    lastHeartbeatMs = now;
    emit("heartbeat", nullptr);
  }
}
