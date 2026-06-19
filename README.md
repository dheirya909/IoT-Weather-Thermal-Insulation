<div align="center">

```diff
████████╗██╗  ██╗███████╗██████╗ ███╗   ███╗ ██████╗ ██████╗ ██╗████████╗
╚══██╔══╝██║  ██║██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██║╚══██╔══╝
   ██║   ███████║█████╗  ██████╔╝██╔████╔██║██║   ██║██████╔╝██║   ██║
   ██║   ██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║
   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██████╔╝██║   ██║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝
```

# The ThermoBit

### IoT-Based Thermal Insulation Analysis Platform

![ESP32](https://img.shields.io/badge/ESP32--C3-Microcontroller-blue?style=for-the-badge)
![DHT11](https://img.shields.io/badge/DHT11-Temperature%20%26%20Humidity-green?style=for-the-badge)
![IoT](https://img.shields.io/badge/Category-IoT-orange?style=for-the-badge)
![Science](https://img.shields.io/badge/Field-Thermal%20Science-red?style=for-the-badge)

</div>

---

## Description

The ThermoBit is an IoT-powered thermal insulation investigation system designed to compare the effectiveness of different insulating materials. Using real-time temperature and humidity measurements, it helps analyze how well materials resist heat transfer and maintain stable internal conditions.

---

## Hardware

| Component        | Purpose                        |
| ---------------- | ------------------------------ |
| ESP32-C3 Mini    | Main Microcontroller           |
| DHT11 Sensor     | Temperature & Humidity Sensing |
| Custom PCB       | Circuit Integration            |
| USB Power Supply | System Power                   |

---

## Connections

| Component Pin | Connected To         |
| ------------- | -------------------- |
| DHT11 VCC     | ESP32-C3 5V          |
| DHT11 GND     | ESP32-C3 GND         |
| DHT11 DATA    | ESP32-C3 GPIO4       |
| LED 1         | ESP32-C3 GPIO6       |
| LED 2         | ESP32-C3 GPIO8       |
| USB Power     | ESP32-C3 Power Input |

---

<div align="center">

### Measure Heat • Compare Materials • Understand Insulation

</div>
