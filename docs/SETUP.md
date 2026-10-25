# Setup

## Hardware

Use a 4 MB ESP32-C3 SuperMini or ESP32-S3 SuperMini with native USB.
Choose the image for the actual chip, not merely the board's appearance.

| Connection | C3 | S3 | C5 receiver |
| --- | --- | --- | --- |
| UART TX via 1 kOhm | GPIO21 | GPIO43 | D10 / GPIO10 |
| Ground | GND | GND | GND |
| BOOT button | GPIO9 | GPIO0 | Not connected |

Use one shared regulated supply in the final installation, or power the
boards independently over USB with common ground. Do not join their 5 V
rails while both USB supplies are connected. No return UART wire is used.
LEDs are unused. This firmware controls channel selection; it does not add OSD.

The C5 needs backpack-capable firmware: V4 #189 or the V5 #271 port. In
V5, D10 must not also have the proposed extra resistor to CVBS fitted.

## Flash a public release

Download and extract the matching `c5vrx-backpack-c3.zip` or
`c5vrx-backpack-s3.zip` from this fork's Releases page. Each contains
the bootloader, partitions, boot_app0, app, a full merged image,
checksums, source commit and verified firmware options.

Install the serial flasher:

```sh
python -m pip install esptool==4.5.1
```

For a C3 (replace COM7 with your port):

```sh
python -m esptool --chip esp32c3 --port COM7 write_flash --flash_mode dio --flash_size 4MB 0x0 firmware-merged.bin
```

Use `--chip esp32s3` for the S3. If automatic reset fails, hold BOOT while
connecting USB, then release it and try again. Reset the board after upload.
The full image overwrites the application and saved device configuration;
it is intended for a fresh setup. SHA256SUMS verifies the extracted files.

## Bind

Public firmware has no phrase or UID compiled in. To use the stock runtime
binding path, power-cycle the backpack three times, allowing setup to run
but keeping each of the first two power-on periods under 30 seconds. Leave
it powered on the third time. USB DEBUG output should show `bindingMode = 1`.
Within two minutes, use the radio's ELRS Backpack binding action to bind
its TX backpack to this VRx backpack. This is backpack binding, separate
from binding the aircraft's ELRS receiver. A short BOOT press opens Wi-Fi
update mode; it is not the bind action. Runtime binding of the generic
release is source-supported but not yet tested on a board for this fork.

Alternatively build with your own phrase locally, matching the TX backpack:
put `-DMY_BINDING_PHRASE="your own phrase"` in the git-ignored
`super_defines.txt`. Do not commit personal settings or redistribute a
bound image. The C5 receiver itself does not need a binding phrase.

## Build locally

```sh
python -m pip install platformio==6.1.19
pio run -e HDZero_ESP32C3_SuperMini_C5VRX_Backpack_DEBUG
pio run -e HDZero_ESP32S3_SuperMini_C5VRX_Backpack_DEBUG
```

Both boards also have `_via_UART` and `_via_WIFI` environments in
`targets/hdzero.ini`. DEBUG uses native USB for diagnostics and UART0
for the C5 link. The DEBUG monitor is 460800 baud; the physical C5 UART
link is 115200 8N1.

```sh
pio run -e HDZero_ESP32C3_SuperMini_C5VRX_Backpack_DEBUG -t upload --upload-port COM7
pio device monitor --port COM7 --baud 460800
```

After binding, use ELRS Lua -> VTX Administrator -> Send VTx. R3 should
echo `SET_CHANNEL_INDEX 34 = R3 5732 MHz`; R5 is index 36, 5806 MHz.
On V5 USB, `U` prints backpack counters and the STATUS channel should
follow. Repeats are sent every two seconds; V5 only acts on a changed
radio channel so a later local selection can stay in effect.
ELRS L channels are refused by C5VRX because its L-band plan is different.

## Package public images

With no active binding/Wi-Fi defines in either configuration file:

```sh
python -m unittest discover -s test -p test_release_guard.py
python tools/package_c5vrx.py --board c3
python tools/package_c5vrx.py --board s3
```

Packaging rejects images with a binding UID, compiled phrase or Wi-Fi
credentials. Outputs are under `dist/` (ignored by Git). CI builds both
boards and performs the same checks before uploading artifacts or
publishing assets for a `backpack-v*` tag.
