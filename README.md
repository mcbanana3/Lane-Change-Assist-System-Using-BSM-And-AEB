# Lane Change Assist (BSM + AEB) - Raspberry Pi

A Raspberry Pi based lane-change assist demo that uses three ultrasonic sensors to estimate front, left, and right distances. The script adapts motor speed, performs emergency braking, and triggers a lane-change maneuver when a side lane is clear. It also provides LED/buzzer alerts and logs telemetry.

## Features

- Blind Spot Monitoring (BSM) using left/right ultrasonic sensors
- Automatic Emergency Braking (AEB) based on front distance and closing rate
- Adaptive speed control for smooth slowdown as obstacles approach
- Simple lane-change assist (left/right) when side lane is clear
- LED + buzzer alert when obstacle is too close
- Logging to a local file for offline analysis

## Project Files

- adas_pro.py: main control script
- adas_log.txt: runtime log file (created automatically)

## Hardware Overview

- Raspberry Pi (BCM pin numbering)
- 4 DC motors (via motor driver) with PWM speed control
- 3 ultrasonic sensors (front, left, right)
- LEDs (red, yellow, green)
- Buzzer

## Pin Mapping (BCM)

### Motor Direction Pins

- M1: (13, 15)
- M2: (18, 16)
- M3: (21, 23)
- M4: (26, 24)

### Motor PWM Pins

- PWM pins: 11, 12, 19, 22

### Ultrasonic Sensors (Trig, Echo)

- Front: (5, 6)
- Left: (17, 27)
- Right: (20, 25)

### Outputs

- LED_RED: 10
- LED_YELLOW: 9
- LED_GREEN: 2
- BUZZER: 3

## How It Works

1. Reads distance from front, left, and right sensors.
2. Computes a simple closing rate from consecutive front readings.
3. Adjusts speed based on front distance:
   - > 60 cm: fast
   - 40-60 cm: medium
   - 25-40 cm: slow
   - 20-25 cm: crawl
   - <= 20 cm: stop + alert
4. If stopped due to obstacle, it attempts a lane change:
   - If left > 40 cm, turn left
   - Else if right > 40 cm, turn right
5. If closing rate is high, applies early braking.

## Software Requirements

- Raspberry Pi OS (or compatible)
- Python 3
- RPi.GPIO library

## Run

From the project directory:

python adas_pro.py

## Logging

The script logs to adas_log.txt with timestamped sensor readings and lane-change events.

## Safety Notes

- This code is for educational and research use only.
- Do not use on public roads or real vehicles.
- Always test on a bench or controlled environment.
- Ensure proper power isolation for motors and sensors.

## Customization Tips

- Tune speed thresholds and duty cycles to match your motor driver and chassis.
- Adjust the lane-change duty cycle balance for smoother turns.
- Increase ultrasonic sample count or timeouts for noisy environments.

## Troubleshooting

- If you see no distance changes, check ultrasonic wiring and power.
- If motors do not spin, verify PWM pins and driver enable pins.
- If the script exits immediately, run as root or check GPIO permissions.
