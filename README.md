# C5VRX Backpack

An unofficial fork of [ExpressLRS/Backpack](https://github.com/ExpressLRS/Backpack)
for an ESP32-C3 or ESP32-S3 SuperMini connected to a C5VRX receiver.
The radio's TX backpack sends the VTX channel over ESP-NOW; this external
backpack forwards HDZero MSPv2 channel commands over a single UART wire.

| Board | UART TX -> C5 D10 through 1 kOhm | BOOT | Evidence |
| --- | --- | --- | --- |
| ESP32-C3 SuperMini (4 MB) | GPIO21 | GPIO9 | Radio -> C3 -> C5VRX-5 R3/R5 channel changes verified 2026-10-25 |
| ESP32-S3 SuperMini (4 MB) | GPIO43 | GPIO0 | Earlier C5VRX-4 bench check 2026-10-07; new generic release needs a board check |

Connect common GND. Use 3.3 V UART logic. On the C5, D10 must be configured
as backpack RX and have no extra DAC resistor fitted. See
[setup, flashing and binding](docs/SETUP.md).
Channel control does not establish video quality or range.

## Firmware

[Releases](https://github.com/LouisHitchcock/C5VRX-Backpack/releases)
provide separate C3 and S3 packages with USB diagnostics. Public images
contain **no binding phrase, binding UID or home Wi-Fi credentials**.
Bind your own unit at runtime or build locally using your own private
`super_defines.txt`. This repository is not an official ExpressLRS or
C5VRX release, and these custom targets are not in the stock configurator.

One-wire mode sends a changed channel twice and repeats the current channel
every two seconds, without waiting for a reply from the C5. C5VRX V5
support is tracked in [PR #271](https://github.com/Twotoz/C5VRX/pull/271),
following [PR #189](https://github.com/Twotoz/C5VRX/pull/189) for V4.
The receiver refuses ELRS L-band channels because its frequency plan differs.

## Attribution and license

ExpressLRS Backpack is developed by **ExpressLRS LLC and its contributors**.
This fork preserves the upstream source history, license and notices.
Its changes add SuperMini targets, a one-wire C5VRX mode and USB diagnostics;
see [PROVENANCE.md](docs/PROVENANCE.md) for revisions and evidence.

This project adapts the backpack integration and bench findings from
[C5VRX](https://github.com/Twotoz/C5VRX) by **Twotoz and the C5VRX contributors**.
Visit the [official C5VRX website](https://twotoz.github.io/C5VRX/) for the
original receiver project and its Discord invite. This derivative is not an
official C5VRX release or endorsed by its authors. The existing GPL-3.0
[LICENSE](LICENSE) applies; C5VRX-derived material is GPL-3.0-only.

## Upstream ExpressLRS Backpack documentation

The original project introduction and links follow.

[![Release](https://img.shields.io/github/v/release/ExpressLRS/Backpack?include_prereleases)](https://github.com/ExpressLRS/Backpack/releases)
[![License](https://img.shields.io/github/license/ExpressLRS/Backpack)](https://github.com/ExpressLRS/Backpack/blob/master/LICENSE)
[![Chat](https://img.shields.io/discord/596350022191415318)](http://discord.gg/dS6ReFY)
[![Open Collective backers](https://img.shields.io/opencollective/backers/expresslrs?label=Open%20Collective%20backers)](https://opencollective.com/expresslrs)

The ExpressLRS Backpack adds ESP-NOW–based wireless communication between ExpressLRS TX modules and compatible FPV hardware, allowing for remote configuration, control, and telemetry exchange. Developed and maintained by **ExpressLRS LLC** and its passionate open source community, working together to advance reliable, high-performance radio control technology.

ExpressLRS Backpack is developed and maintained by **ExpressLRS LLC** and its passionate open source community, working together to advance reliable, high-performance radio control technology.

## What is a "TX Backpack"?

Some of the ExpressLRS TX modules include an additional ESP8285 chip, which lets us communicate wirelessly with other ESP8285 enabled devices using a protocol called espnow. We call this chip the "TX-Backpack". The aim of the TX-Backpack is to allow wireless communication between ExpressLRS, and other FPV related devices for command and control, or for querying config.

## Sounds interesting... What type of FPV devices can it talk to?
 A prime use case is your video receiver module (or VRX). Currently there aren't many VRX modules that have an ESP8285 built in to allow them to communicate with ExpressLRS, so in most cases you need to add your own. A small ESP based receiver can be "piggybacked" onto your VRX module, which allows ExpressLRS to control the band and channel that your goggles are set to. We call this device the "VRX-Backpack". 

## Wow cool, so I'll be able to control the module via ELRS!? Which VRX modules does it work with?
The list of supported modules can be found on the wiki:
https://github.com/ExpressLRS/Backpack/wiki

## Great! I use one of the supported modules. How do I get a VRX-Backpack?
There are a few different options for both DIY or compatible off the shelf backpacks... check the wiki for the current list:
https://github.com/ExpressLRS/Backpack/wiki
