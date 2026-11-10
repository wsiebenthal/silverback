# Sensor firmware

ESP32 sketch that reads a digital PIR pin and writes Silver Back events to USB serial. The event text is specified in [docs/protocol.md](../docs/protocol.md).

This build is USB serial only. BLE, Wi-Fi, time-of-flight, and sleep are tracked in [ROADMAP.md](../ROADMAP.md).

## Wiring

Reference design for an ESP32 dev board and an HC-SR501. This is a bench circuit, not a finished product.

```
USB host (computer)          ESP32                      HC-SR501
      |                      GPIO 27 <------------------ OUT
      | USB serial           GND ------------------------ GND
      |--------------------  5V or VIN ----------------> VCC
```

ESP32 GPIO pins are not 5 V tolerant. Power the HC-SR501 from 5 V (its VCC range is typically about 4.5 V to 20 V) and measure OUT before you connect it. Many modules drive OUT to about 3.3 V. If a meter shows 5 V on OUT, put a divider or a level shifter in series (for example 10 kΩ from OUT to the GPIO and 20 kΩ from the GPIO to ground) before trusting the pin.

GPIO 27 uses the internal pulldown, so an open connector reads LOW and the sketch reports `clear` after the debounce. The module has to drive the pin HIGH for `approach`.

The onboard LED on GPIO 2 follows the debounced level (HIGH while occupied). LED polarity differs across dev boards; the serial line is the real interface. Set `SILVERBACK_LED_PIN` to `-1` in `platformio.ini` to disable it.

HC-SR501 modules often need up to a minute after power-up before the output means anything, and the two pots set sensitivity and hold time. The sketch reports edges during that warmup. It does not suppress them.

## Build

The project is set up for [PlatformIO](https://platformio.org/). From this directory:

```bash
pio run -e esp32dev
pio run -e esp32dev -t upload
pio device monitor -b 115200
```

`platformio.ini` pins `espressif32` 8.0.0. `pio run -e esp32dev` completes with that pin; the image was not flashed to a board. `src/main.cpp` is a single Arduino sketch with no libraries, so the Arduino IDE can compile it too if an ESP32 board package is installed. A host-side unit test reads the sketch to check that the event vocabulary is still there.

Pins and the LED live in `platformio.ini` as build flags (`SILVERBACK_PIR_PIN`, `SILVERBACK_LED_PIN`). Active level defaults to `HIGH` inside the sketch (`SILVERBACK_PIR_ACTIVE`).

## What you should see

After reset, a line like:

```json
{"v":1,"type":"hello","sensor":"pir","transport":"usb-serial","fw":"0.1.0","seq":0,"uptime_ms":1}
```

About 200 ms later, a `presence` event for the level on the pin (`approach` when it is HIGH, `clear` when it is LOW). Further edges emit another `presence` line. A `heartbeat` line follows every 30 seconds. A sample session is in [docs/examples/session.ndjson](../docs/examples/session.ndjson).

Point the sensor at the entrance to the desk or cubicle, not at the person who is already sitting there. The firmware cannot tell those two motions apart.
